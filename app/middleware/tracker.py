"""
Server Behavior Tracker — Main Middleware.

This middleware captures comprehensive behavioral data for every HTTP request:
  ✓ Request timing (start, end, duration)
  ✓ Request/response sizes
  ✓ Client identity (IP, User-Agent, authenticated user)
  ✓ Status codes and error detection
  ✓ Process resource usage (CPU, memory, concurrency)
  ✓ Prometheus metrics
  ✓ Structured JSON file logging
  ✓ Pretty console output (dev mode)

NOTE: This middleware handles HTTP requests only. WebSocket connections
are tracked separately via explicit lifecycle logging in the endpoint handler
(FastAPI's @app.middleware("http") does not fire for WebSocket upgrades).
"""

import json
import logging
import logging.handlers
import os
import time

from fastapi import Request, Response

from app.config import settings as app_config
from app.security import get_client_ip

from .context import (
    request_id_var,
    client_ip_var,
    user_var,
    generate_request_id,
)
from .sanitizer import (
    safe_parse_body,
    redact_query_params,
    truncate_for_console,
)
from .resources import resource_monitor
from .metrics import metrics
from .active_users import active_user_tracker


# ─── Logging Setup ────────────────────────────────────────────────────────────
_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(_LOG_DIR, exist_ok=True)

# Structured JSON loggers — one per concern
_loggers: dict[str, logging.Logger] = {}


def _get_logger(name: str, filename: str) -> logging.Logger:
    """Get or create a rotating file logger."""
    if name not in _loggers:
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.handlers.RotatingFileHandler(
                os.path.join(_LOG_DIR, filename),
                maxBytes=10_000_000,   # 10 MB per file
                backupCount=5,
                encoding="utf-8",
            )
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        _loggers[name] = logger
    return _loggers[name]


request_logger   = _get_logger("onfood.request",   "request.log")
response_logger  = _get_logger("onfood.response",  "response.log")
behavior_logger  = _get_logger("onfood.behavior",  "behavior.log")
error_logger     = _get_logger("onfood.errors",    "errors.log")


# ─── Console Colors ──────────────────────────────────────────────────────────
_C = {
    "reset":   "\033[0m",
    "bold":    "\033[1m",
    "green":   "\033[92m",
    "yellow":  "\033[93m",
    "red":     "\033[91m",
    "cyan":    "\033[96m",
    "grey":    "\033[90m",
    "blue":    "\033[94m",
    "magenta": "\033[95m",
    "white":   "\033[97m",
}

# Paths whose request/response logging is suppressed (static files, health check)
_SKIP_LOG_PREFIXES = ("/icons/", "/images/", "/sounds/", "/favicon", "/metrics")


def _status_color(status: int) -> str:
    if status < 300:
        return _C["green"]
    if status < 400:
        return _C["yellow"]
    return _C["red"]


def _method_color(method: str) -> str:
    return {
        "GET":    _C["cyan"],
        "POST":   _C["green"],
        "PATCH":  _C["yellow"],
        "PUT":    _C["yellow"],
        "DELETE": _C["red"],
    }.get(method, _C["reset"])


def _severity_icon(status: int, duration_ms: float, slow_threshold: float) -> str:
    """Return an emoji severity indicator for console output."""
    if status >= 500:
        return "🔴"
    if status >= 400:
        return "🟡"
    if duration_ms > slow_threshold * 2:
        return "🐢"
    if duration_ms > slow_threshold:
        return "⚠️"
    return "🟢"


# ─── Route Template Normalization ─────────────────────────────────────────────
def _normalize_path(request: Request) -> str:
    """
    Get the matched route template (e.g., /api/orders/{orderId}) instead of the
    raw path (/api/orders/abc-123) to avoid cardinality explosion in metrics.

    Falls back to the raw path if no matched route.
    """
    route = request.scope.get("route")
    if route and hasattr(route, "path"):
        return route.path
    return request.url.path


# ─── Extract User Context ────────────────────────────────────────────────────
def _extract_user_from_request(request: Request) -> dict:
    """
    Try to extract user identity from the Authorization header JWT without
    blocking. This is best-effort — the actual auth validation happens in
    the route dependency, not here.

    WARNING: This decodes JWT without signature verification. The logged
    user_id may reflect forged/expired tokens. Do NOT use user_id from logs
    for security decisions.
    """
    auth_header = request.headers.get("authorization", "")
    if not auth_header.lower().startswith("bearer "):
        return {}
    token = auth_header[7:].strip()
    if not token:
        return {}
    try:
        import jwt as pyjwt
        # Decode without verification (we only need the claims for logging,
        # not security). The route's actual Depends() handles validation.
        payload = pyjwt.decode(token, options={"verify_signature": False})
        return {
            "user_id": str(payload.get("sub", "")),
            "role": payload.get("role", ""),
            "canteen_id": payload.get("canteen_id", ""),
        }
    except Exception:
        return {}


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN MIDDLEWARE FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

async def server_behavior_tracker(request: Request, call_next):
    """
    FastAPI HTTP middleware that captures comprehensive server behavior data.

    This single middleware replaces the old `dev_request_logger` in main.py
    and adds resource tracking, Prometheus metrics, and structured behavior logs.
    """

    # Read config-driven threshold (never hardcoded)
    slow_threshold_ms = getattr(app_config, "SLOW_REQUEST_THRESHOLD_MS", 500)

    # ── 1. Generate / propagate request ID ────────────────────────────────────
    incoming_req_id = request.headers.get("X-Request-Id")
    req_id = generate_request_id(incoming_req_id)
    request.state.request_id = req_id

    # ── 2. Resolve client IP ─────────────────────────────────────────────────
    client_ip = get_client_ip(request)

    # ── 3. Extract user context (best-effort, non-blocking) ──────────────────
    user_ctx = _extract_user_from_request(request)
    if user_ctx.get("user_id"):
        active_user_tracker.record_activity(
            user_id=user_ctx["user_id"],
            role=user_ctx.get("role", ""),
            canteen_id=user_ctx.get("canteen_id", ""),
            client_ip=client_ip,
            user_agent=request.headers.get("user-agent", ""),
            path=request.url.path,
            method=request.method,
        )

    # ── 4. Set context variables (available everywhere in this request) ──────
    req_id_token = request_id_var.set(req_id)
    ip_token = client_ip_var.set(client_ip)
    user_token = user_var.set(user_ctx)

    # ── 5. Track resources ───────────────────────────────────────────────────
    in_flight = resource_monitor.request_started()
    metrics.set_in_progress(in_flight)
    resource_before = resource_monitor.snapshot()

    # ── 6. Read request body for logging ─────────────────────────────────────
    request_body = await request.body()
    request_size = len(request_body)

    # ── 7. Start timer ───────────────────────────────────────────────────────
    started = time.perf_counter()

    path = request.url.path
    method = request.method
    skip_verbose = any(path.startswith(p) for p in _SKIP_LOG_PREFIXES) or path == "/"

    # ── 8. Print incoming request to console (dev mode) ──────────────────────
    if not skip_verbose:
        body_preview = ""
        if request_body:
            try:
                parsed = safe_parse_body(request_body)
                body_str = json.dumps(parsed, ensure_ascii=False)
                body_preview = f"\n    {_C['grey']}Body: {truncate_for_console(body_str)}{_C['reset']}"
            except Exception:
                pass

        safe_qs = redact_query_params(dict(request.query_params))
        qs_str = ("?" + "&".join(f"{k}={v}" for k, v in safe_qs.items())) if safe_qs else ""

        user_tag = ""
        if user_ctx.get("user_id"):
            user_tag = f" {_C['magenta']}[user:{user_ctx['user_id'][:8]}]{_C['reset']}"

        print(
            f"  {_C['grey']}>> [{req_id}]{_C['reset']} [{_C['magenta']}{client_ip}{_C['reset']}]"
            f"{user_tag} "
            f"{_method_color(method)}{_C['bold']}{method}{_C['reset']} "
            f"{_C['blue']}{path}{qs_str}{_C['reset']}"
            f" {_C['grey']}(in-flight: {in_flight}){_C['reset']}"
            f"{body_preview}",
            flush=True,
        )

    # ── 9. Execute the actual route handler ──────────────────────────────────
    try:
        response = await call_next(request)
    except Exception as exc:
        # Unhandled exception that escaped all exception handlers
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        resource_monitor.request_finished()

        error_logger.error(json.dumps({
            "req_id": req_id,
            "event": "unhandled_exception",
            "method": method,
            "path": path,
            "client_ip": client_ip,
            "user": user_ctx,
            "error": str(exc),
            "error_type": type(exc).__name__,
            "duration_ms": duration_ms,
        }, ensure_ascii=False, default=str))

        # Reset context variables before re-raising
        request_id_var.reset(req_id_token)
        client_ip_var.reset(ip_token)
        user_var.reset(user_token)

        # Re-raise so FastAPI's exception handlers can deal with it
        raise

    # ── 10. Measure duration ─────────────────────────────────────────────────
    duration_seconds = time.perf_counter() - started
    duration_ms = round(duration_seconds * 1000, 2)

    # ── 11. Resource snapshot after processing ───────────────────────────────
    remaining = resource_monitor.request_finished()
    resource_after = resource_monitor.snapshot()

    # ── 12. Attach tracing headers to response ───────────────────────────────
    response.headers["X-Request-Id"] = req_id
    response.headers["X-Response-Time-Ms"] = str(duration_ms)

    # Security headers (on every response)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    if app_config.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # ── 13. Capture response body (skip SSE/streaming) ───────────────────────
    content_type = response.headers.get("content-type", "")
    is_streaming = "text/event-stream" in content_type or "multipart/" in content_type

    response_body = None
    response_size = 0
    if not is_streaming and hasattr(response, "body_iterator"):
        chunks = []
        async for chunk in response.body_iterator:
            chunks.append(chunk if isinstance(chunk, bytes) else chunk.encode("utf-8"))
        response_body = b"".join(chunks)
        response_size = len(response_body)
        response = Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
            background=response.background,
        )
    elif hasattr(response, "body"):
        response_body = response.body
        response_size = len(response_body) if response_body else 0

    status = response.status_code

    # ── 14. Record Prometheus metrics ────────────────────────────────────────
    path_template = _normalize_path(request)
    metrics.record_request(method, path_template, status, duration_seconds)
    metrics.set_in_progress(remaining)
    metrics.set_resources(
        resource_after.memory_rss_mb * 1024 * 1024,  # convert to bytes
        resource_after.cpu_percent,
    )

    # ── 15. Console output (dev mode) ────────────────────────────────────────
    if not skip_verbose:
        icon = _severity_icon(status, duration_ms, slow_threshold_ms)
        slow_warn = f" {_C['yellow']}SLOW{_C['reset']}" if duration_ms > slow_threshold_ms else ""

        resp_preview = ""
        if response_body:
            try:
                parsed = safe_parse_body(response_body)
                resp_str = json.dumps(parsed, ensure_ascii=False)
                resp_preview = f"\n    {_C['grey']}Body: {truncate_for_console(resp_str)}{_C['reset']}"
            except Exception:
                pass

        mem_delta = resource_after.memory_rss_mb - resource_before.memory_rss_mb
        mem_info = f" {_C['grey']}mem:{resource_after.memory_rss_mb}MB"
        if abs(mem_delta) > 1:
            mem_info += f" (Δ{mem_delta:+.1f}MB)"
        mem_info += _C['reset']

        print(
            f"  {_C['grey']}<< [{req_id}]{_C['reset']} {icon} "
            f"{_status_color(status)}{_C['bold']}{status}{_C['reset']} "
            f"{_C['grey']}{duration_ms}ms{_C['reset']}"
            f"{slow_warn}"
            f" {_C['grey']}({request_size}B → {response_size}B){_C['reset']}"
            f"{mem_info}"
            f"{resp_preview}",
            flush=True,
        )

    # ── 16. Structured JSON file logging ─────────────────────────────────────
    is_production = app_config.ENVIRONMENT == "production"
    safe_query = redact_query_params(dict(request.query_params))

    # Request log
    request_logger.info(json.dumps({
        "req_id": req_id,
        "event": "http_request",
        "client_ip": client_ip,
        "user": user_ctx if user_ctx else None,
        "method": method,
        "path": path,
        "path_template": path_template,
        "query": safe_query if safe_query else None,
        "user_agent": request.headers.get("user-agent", ""),
        "content_length": request_size,
        "request_json": None if is_production else safe_parse_body(request_body),
    }, ensure_ascii=False, default=str))

    # Response log
    response_logger.info(json.dumps({
        "req_id": req_id,
        "event": "http_response",
        "client_ip": client_ip,
        "method": method,
        "path": path,
        "path_template": path_template,
        "status": status,
        "duration_ms": duration_ms,
        "request_bytes": request_size,
        "response_bytes": response_size,
        "response_json": None if is_production else safe_parse_body(response_body),
    }, ensure_ascii=False, default=str))

    # Behavior / resource log (always, even in production)
    behavior_logger.info(json.dumps({
        "req_id": req_id,
        "event": "request_behavior",
        "method": method,
        "path_template": path_template,
        "status": status,
        "duration_ms": duration_ms,
        "in_flight_at_start": resource_before.in_flight_requests,
        "in_flight_at_end": remaining,
        "memory_rss_mb": resource_after.memory_rss_mb,
        "cpu_percent": resource_after.cpu_percent,
        "request_bytes": request_size,
        "response_bytes": response_size,
        "is_slow": duration_ms > slow_threshold_ms,
        "is_error": status >= 500,
        "client_ip": client_ip,
        "user_id": user_ctx.get("user_id", ""),
    }, ensure_ascii=False, default=str))

    # ── 17. Reset context variables (cleanup) ────────────────────────────────
    request_id_var.reset(req_id_token)
    client_ip_var.reset(ip_token)
    user_var.reset(user_token)

    return response
