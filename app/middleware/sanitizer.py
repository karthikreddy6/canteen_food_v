"""
Data sanitizer for safe logging.

Ensures passwords, tokens, OTPs, and other credentials are redacted from
request/response bodies and query parameters before they reach any log file.

SECURITY GUARANTEE: Raw Authorization, Cookie, and X-App-Key header values
are NEVER logged by any component using this module. Only decoded,
non-sensitive JWT claims (sub, role) are written to logs.
"""

import json
from typing import Any


# ─── Sensitive Key Detection ─────────────────────────────────────────────────
# Any JSON key whose lowercase matches one of these will have its value
# replaced with "[REDACTED]" in all log output.
SENSITIVE_KEYS: set[str] = {
    "password",
    "otp",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "hashed_password",
    "secret",
    "api_key",
    "app_key",
}

# Query parameter names that should be redacted (e.g., ?token=<JWT> for SSE/WS)
SENSITIVE_QUERY_PARAMS: set[str] = {
    "token",
    "access_token",
}

# HTTP header names whose values must NEVER appear in logs
SENSITIVE_HEADERS: set[str] = {
    "authorization",
    "cookie",
    "x-app-key",
}


def redact_dict(data: Any) -> Any:
    """
    Recursively walk a dict/list and replace values of sensitive keys with
    "[REDACTED]".

    Examples:
        >>> redact_dict({"email": "a@b.com", "password": "secret123"})
        {'email': 'a@b.com', 'password': '[REDACTED]'}

        >>> redact_dict({"user": {"token": "abc123"}})
        {'user': {'token': '[REDACTED]'}}
    """
    if isinstance(data, dict):
        return {
            key: "[REDACTED]" if key.lower() in SENSITIVE_KEYS else redact_dict(value)
            for key, value in data.items()
        }
    if isinstance(data, list):
        return [redact_dict(item) for item in data]
    return data


def safe_parse_body(raw_body: bytes | None) -> Any:
    """
    Attempt to parse raw bytes as JSON and redact sensitive fields.
    Returns None for empty bodies, "[non-json body]" for unparseable content.
    """
    if not raw_body:
        return None
    try:
        parsed = json.loads(raw_body)
        return redact_dict(parsed)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "[non-json body]"


def redact_query_params(params: dict[str, str]) -> dict[str, str]:
    """
    Redact sensitive query parameter values.

    Example:
        >>> redact_query_params({"page": "1", "token": "eyJhbG..."})
        {'page': '1', 'token': '[REDACTED]'}
    """
    return {
        key: "[REDACTED]" if key.lower() in SENSITIVE_QUERY_PARAMS else value
        for key, value in params.items()
    }


def is_sensitive_header(header_name: str) -> bool:
    """Check if a header name is sensitive and should never be logged."""
    return header_name.lower() in SENSITIVE_HEADERS


def truncate_for_console(text: str, max_length: int = 300) -> str:
    """Truncate text for console display, appending '…' if truncated."""
    if len(text) > max_length:
        return text[:max_length] + "…"
    return text
