import asyncio
import datetime
from collections import defaultdict

from fastapi import HTTPException, status


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