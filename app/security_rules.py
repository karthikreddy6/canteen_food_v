import asyncio
import datetime
import hashlib
import logging
from collections import defaultdict

from fastapi import HTTPException, Request, status

_rules_logger = logging.getLogger("onfood.security_rules")


# ─── Per-IP account-switching limit ─────────────────────────────────────────
# Prevents a single IP from cycling through many different accounts in a short
# time (e.g. credential stuffing with many targets).

WINDOW = datetime.timedelta(minutes=30)
MAX_ACCOUNTS_PER_IP = 2

_ip_accounts: dict[str, list[tuple[datetime.datetime, str]]] = defaultdict(list)
_lock = asyncio.Lock()


async def enforce_ip_account_limit(ip_address: str, account_key: str) -> None:
    """Limit one IP address to two different accounts within a 30 minute window."""
    now = datetime.datetime.now(datetime.timezone.utc)
    account_key = account_key.strip().lower()

    async with _lock:
        recent_events = [
            event
            for event in _ip_accounts[ip_address]
            if now - event[0] <= WINDOW
        ]
        recent_accounts = {event_account for _, event_account in recent_events}

        if account_key not in recent_accounts and len(recent_accounts) >= MAX_ACCOUNTS_PER_IP:
            _ip_accounts[ip_address] = recent_events
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many accounts used from this IP address. Try again after 30 minutes.",
            )

        recent_events.append((now, account_key))
        _ip_accounts[ip_address] = recent_events


# ─── Per-IP login / OTP brute-force rate limit ──────────────────────────────
# Prevents password guessing and OTP enumeration by capping the number of
# auth attempts per IP within a sliding window.
#
# When CACHE_REDIS_URL is configured the counter is stored in Redis so it is
# shared across multiple Uvicorn workers. Otherwise an in-process dict is used
# (suitable for single-worker development deployments).

_LOGIN_WINDOW_SECONDS = 15 * 60   # 15 minutes
_LOGIN_MAX_ATTEMPTS = 10           # max attempts per IP per window

# ── In-process fallback store ──
_login_attempts: dict[str, list[datetime.datetime]] = defaultdict(list)
_login_lock = asyncio.Lock()


_redis_pool = None


def _get_redis_client(redis_url: str):
    global _redis_pool
    if _redis_pool is None:
        import redis.asyncio as aioredis
        _redis_pool = aioredis.from_url(redis_url, decode_responses=True)
    return _redis_pool


async def _redis_rate_limit_login(redis_url: str, ip: str) -> None:
    """Redis-backed sliding-window counter (multi-worker safe)."""
    try:
        r = _get_redis_client(redis_url)
        key = f"onfood:login_attempts:{ip}"
        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        window_start = now_ts - _LOGIN_WINDOW_SECONDS

        async with r.pipeline() as pipe:
            await pipe.zremrangebyscore(key, "-inf", window_start)
            await pipe.zcard(key)
            await pipe.zadd(key, {str(now_ts): now_ts})
            await pipe.expire(key, _LOGIN_WINDOW_SECONDS + 10)
            results = await pipe.execute()

        attempt_count = results[1]
        if attempt_count >= _LOGIN_MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Too many login attempts from this IP. "
                    f"Please wait {_LOGIN_WINDOW_SECONDS // 60} minutes and try again."
                ),
            )
    except HTTPException:
        raise
    except Exception as exc:
        _rules_logger.error("Redis rate-limit error (falling back to in-process): %s", exc)
        await _inprocess_rate_limit_login(ip)


async def _inprocess_rate_limit_login(ip: str) -> None:
    """In-process sliding-window counter (single-worker / development only)."""
    now = datetime.datetime.now(datetime.timezone.utc)
    window_start = now - datetime.timedelta(seconds=_LOGIN_WINDOW_SECONDS)

    async with _login_lock:
        recent = [t for t in _login_attempts[ip] if t >= window_start]
        if len(recent) >= _LOGIN_MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Too many login attempts from this IP. "
                    f"Please wait {_LOGIN_WINDOW_SECONDS // 60} minutes and try again."
                ),
            )
        recent.append(now)
        _login_attempts[ip] = recent


async def rate_limit_login(ip: str) -> None:
    """
    Enforce a per-IP brute-force limit on authentication endpoints.
    Uses Redis when CACHE_REDIS_URL is set; otherwise falls back to in-process.
    """
    from app.config import settings
    if settings.CACHE_REDIS_URL:
        await _redis_rate_limit_login(settings.CACHE_REDIS_URL, ip)
    else:
        await _inprocess_rate_limit_login(ip)


# ─── Per-account (email) login rate limit ────────────────────────────────────
# Protects against distributed attacks that rotate IPs but target the same
# account (e.g. slow password spray from a botnet on campus Wi-Fi).
# Runs in parallel with the per-IP limiter.

_ACCOUNT_LOGIN_WINDOW_SECONDS = 15 * 60   # 15 minutes
_ACCOUNT_LOGIN_MAX_ATTEMPTS = 15           # slightly higher than IP limit

_account_login_attempts: dict[str, list[datetime.datetime]] = defaultdict(list)
_account_login_lock = asyncio.Lock()


def _email_key(email: str) -> str:
    """Hash email so plain addresses aren't persisted in memory."""
    return hashlib.sha256(email.strip().lower().encode()).hexdigest()[:16]


async def _redis_rate_limit_login_account(redis_url: str, email: str) -> None:
    try:
        r = _get_redis_client(redis_url)
        key = f"onfood:login_attempts:account:{_email_key(email)}"
        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        window_start = now_ts - _ACCOUNT_LOGIN_WINDOW_SECONDS

        async with r.pipeline() as pipe:
            await pipe.zremrangebyscore(key, "-inf", window_start)
            await pipe.zcard(key)
            await pipe.zadd(key, {str(now_ts): now_ts})
            await pipe.expire(key, _ACCOUNT_LOGIN_WINDOW_SECONDS + 10)
            results = await pipe.execute()

        attempt_count = results[1]
        if attempt_count >= _ACCOUNT_LOGIN_MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    "Too many login attempts for this account. "
                    f"Please wait {_ACCOUNT_LOGIN_WINDOW_SECONDS // 60} minutes and try again."
                ),
            )
    except HTTPException:
        raise
    except Exception as exc:
        _rules_logger.error("Redis account rate-limit error (falling back): %s", exc)
        await _inprocess_rate_limit_login_account(email)


async def _inprocess_rate_limit_login_account(email: str) -> None:
    now = datetime.datetime.now(datetime.timezone.utc)
    window_start = now - datetime.timedelta(seconds=_ACCOUNT_LOGIN_WINDOW_SECONDS)
    key = _email_key(email)

    async with _account_login_lock:
        recent = [t for t in _account_login_attempts[key] if t >= window_start]
        if len(recent) >= _ACCOUNT_LOGIN_MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    "Too many login attempts for this account. "
                    f"Please wait {_ACCOUNT_LOGIN_WINDOW_SECONDS // 60} minutes and try again."
                ),
            )
        recent.append(now)
        _account_login_attempts[key] = recent


async def rate_limit_login_by_account(email: str) -> None:
    """
    Per-account (email) brute-force limit running alongside the IP limiter.
    Stops distributed attacks that rotate IPs but target one account.
    """
    from app.config import settings
    if settings.CACHE_REDIS_URL:
        await _redis_rate_limit_login_account(settings.CACHE_REDIS_URL, email)
    else:
        await _inprocess_rate_limit_login_account(email)


# ─── Per-phone OTP send throttle ─────────────────────────────────────────────
# Stops OTP-bombing harassment and controls WhatsApp API costs.
# Max 3 OTP sends per phone number per 60 minutes.

_OTP_WINDOW_SECONDS = 60 * 60   # 1 hour
_OTP_MAX_SENDS = 3

_otp_sends: dict[str, list[datetime.datetime]] = defaultdict(list)
_otp_lock = asyncio.Lock()


async def _redis_throttle_otp(redis_url: str, phone: str) -> None:
    try:
        r = _get_redis_client(redis_url)
        key = f"onfood:otp_sends:{phone}"
        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        window_start = now_ts - _OTP_WINDOW_SECONDS

        async with r.pipeline() as pipe:
            await pipe.zremrangebyscore(key, "-inf", window_start)
            await pipe.zcard(key)
            await pipe.zadd(key, {str(now_ts): now_ts})
            await pipe.expire(key, _OTP_WINDOW_SECONDS + 10)
            results = await pipe.execute()

        send_count = results[1]
        if send_count >= _OTP_MAX_SENDS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many OTP requests for this number. Please wait 1 hour and try again.",
            )
    except HTTPException:
        raise
    except Exception as exc:
        _rules_logger.error("Redis OTP throttle error (falling back): %s", exc)
        await _inprocess_throttle_otp(phone)


async def _inprocess_throttle_otp(phone: str) -> None:
    now = datetime.datetime.now(datetime.timezone.utc)
    window_start = now - datetime.timedelta(seconds=_OTP_WINDOW_SECONDS)

    async with _otp_lock:
        recent = [t for t in _otp_sends[phone] if t >= window_start]
        if len(recent) >= _OTP_MAX_SENDS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many OTP requests for this number. Please wait 1 hour and try again.",
            )
        recent.append(now)
        _otp_sends[phone] = recent


async def throttle_otp_per_phone(phone: str) -> None:
    """
    Rate-limit OTP sends per phone number (max 3 per hour).
    Prevents OTP-bombing harassment and WhatsApp API cost abuse.
    """
    from app.config import settings
    if settings.CACHE_REDIS_URL:
        await _redis_throttle_otp(settings.CACHE_REDIS_URL, phone)
    else:
        await _inprocess_throttle_otp(phone)


# ─── College suggest rate limit ──────────────────────────────────────────────
# The POST /api/locations/colleges/suggest endpoint is public (no auth).
# Limit to 5 suggestions per IP per hour to prevent DB spam.

_SUGGEST_WINDOW_SECONDS = 60 * 60   # 1 hour
_SUGGEST_MAX_PER_IP = 5

_suggest_attempts: dict[str, list[datetime.datetime]] = defaultdict(list)
_suggest_lock = asyncio.Lock()


async def _redis_rate_limit_suggest(redis_url: str, ip: str) -> None:
    try:
        r = _get_redis_client(redis_url)
        key = f"onfood:college_suggest:{ip}"
        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        window_start = now_ts - _SUGGEST_WINDOW_SECONDS

        async with r.pipeline() as pipe:
            await pipe.zremrangebyscore(key, "-inf", window_start)
            await pipe.zcard(key)
            await pipe.zadd(key, {str(now_ts): now_ts})
            await pipe.expire(key, _SUGGEST_WINDOW_SECONDS + 10)
            results = await pipe.execute()

        count = results[1]
        if count >= _SUGGEST_MAX_PER_IP:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many college suggestions from this IP. Please wait 1 hour.",
            )
    except HTTPException:
        raise
    except Exception as exc:
        _rules_logger.error("Redis suggest rate-limit error (falling back): %s", exc)
        await _inprocess_rate_limit_suggest(ip)
    except HTTPException:
        raise
    except Exception as exc:
        _rules_logger.error("Redis suggest rate-limit error (falling back): %s", exc)
        await _inprocess_rate_limit_suggest(ip)


async def _inprocess_rate_limit_suggest(ip: str) -> None:
    now = datetime.datetime.now(datetime.timezone.utc)
    window_start = now - datetime.timedelta(seconds=_SUGGEST_WINDOW_SECONDS)

    async with _suggest_lock:
        recent = [t for t in _suggest_attempts[ip] if t >= window_start]
        if len(recent) >= _SUGGEST_MAX_PER_IP:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many college suggestions from this IP. Please wait 1 hour.",
            )
        recent.append(now)
        _suggest_attempts[ip] = recent


async def rate_limit_college_suggest(ip: str) -> None:
    """Rate-limit unauthenticated college suggest endpoint (5 per IP per hour)."""
    from app.config import settings
    if settings.CACHE_REDIS_URL:
        await _redis_rate_limit_suggest(settings.CACHE_REDIS_URL, ip)
    else:
        await _inprocess_rate_limit_suggest(ip)