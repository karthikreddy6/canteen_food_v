"""
Request-scoped context variables.

These ContextVars are set by the tracker middleware at the start of each
request and are automatically available in every function, log call, and
database query within that same async task — no manual passing required.

Usage from anywhere in the codebase:
    from app.middleware.context import request_id_var, client_ip_var, user_var
    print(f"Current request: {request_id_var.get('?')}")
"""

import logging
import uuid
from contextvars import ContextVar


# ─── Context Variables ────────────────────────────────────────────────────────
# These are set per-request by the tracker middleware and cleared afterward.

# Unique correlation ID for the request (8-char short UUID or propagated X-Request-Id)
request_id_var: ContextVar[str] = ContextVar("request_id", default="")

# Resolved client IP (from CF-Connecting-IP, X-Forwarded-For, or socket peer)
client_ip_var: ContextVar[str] = ContextVar("client_ip", default="")

# Authenticated user context: {"user_id": "...", "role": "...", "canteen_id": "..."}
# Empty dict when unauthenticated.
user_var: ContextVar[dict] = ContextVar("user_ctx", default={})


# ─── Logging Integration ─────────────────────────────────────────────────────
# This custom LogRecord factory injects [req_id] and [client_ip] into EVERY log
# line automatically, so even logs from SQLAlchemy, httpx, or third-party code
# will include the request correlation ID.

_original_factory = logging.getLogRecordFactory()


def _context_log_factory(*args, **kwargs):
    """Custom LogRecord factory that adds request context to all log records."""
    record = _original_factory(*args, **kwargs)
    record.req_id = request_id_var.get("")
    record.client_ip = client_ip_var.get("")
    user = user_var.get({})
    record.user_id = user.get("user_id", "")
    record.user_role = user.get("role", "")
    return record


def install_context_logging():
    """
    Call once at startup to inject request context into all Python log records.

    After calling this, you can use %(req_id)s and %(client_ip)s in any
    logging format string across the entire application.

    Example formatter:
        "%(asctime)s [%(req_id)s] [%(client_ip)s] %(levelname)s %(message)s"
    """
    logging.setLogRecordFactory(_context_log_factory)


def generate_request_id(request_header_value: str | None = None) -> str:
    """
    Generate or propagate a request correlation ID.

    If the client sent an X-Request-Id header, we honor it (for end-to-end
    tracing). Otherwise, generate a short 8-character UUID.
    """
    if request_header_value:
        # Sanitize: only allow alphanumeric, hyphens, and underscores
        sanitized = "".join(
            c for c in request_header_value[:64]
            if c.isalnum() or c in "-_"
        )
        if sanitized:
            return sanitized
    return str(uuid.uuid4())[:8]
