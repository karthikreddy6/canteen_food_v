"""
Tests for the Server Behavior Tracking Middleware.

Uses the existing async_client fixture from conftest.py (httpx.AsyncClient + ASGITransport)
for consistency with the rest of the test suite.
"""

import json
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Re-use the project's existing conftest pattern
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Disable order cooldown during testing
os.environ["ORDER_COOLDOWN_SECONDS"] = "0"

from app.main import app
from app.middleware.sanitizer import redact_dict, safe_parse_body, redact_query_params
from app.middleware.resources import ResourceMonitor, ResourceSnapshot
from app.middleware.context import generate_request_id

CLIENT_HEADERS = {
    "X-App-Key": "ONFOOD_SECURE_CLIENT_APP_KEY_2026",
    "Content-Type": "application/json",
}


# ─── Fixture ─────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture(loop_scope="module")
async def client():
    """Provides an HTTPX AsyncClient bound to the FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers=CLIENT_HEADERS,
    ) as c:
        yield c


# ─── Response Header Tests ──────────────────────────────────────────────────

@pytest.mark.asyncio(loop_scope="module")
async def test_response_has_request_id_header(client):
    """Every response must include an X-Request-Id header."""
    response = await client.get("/")
    assert "X-Request-Id" in response.headers
    assert len(response.headers["X-Request-Id"]) > 0


@pytest.mark.asyncio(loop_scope="module")
async def test_response_has_response_time_header(client):
    """Every response must include X-Response-Time-Ms."""
    response = await client.get("/")
    assert "X-Response-Time-Ms" in response.headers
    # Should be a valid float
    float(response.headers["X-Response-Time-Ms"])


@pytest.mark.asyncio(loop_scope="module")
async def test_security_headers_present(client):
    """Security headers must be set on every response."""
    response = await client.get("/")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("Referrer-Policy") == "no-referrer"


@pytest.mark.asyncio(loop_scope="module")
async def test_request_id_propagation(client):
    """Client-supplied X-Request-Id should be echoed back."""
    custom_id = "my-trace-id-123"
    response = await client.get("/", headers={"X-Request-Id": custom_id})
    assert response.headers["X-Request-Id"] == custom_id


# ─── Sanitizer Unit Tests ───────────────────────────────────────────────────

def test_redact_dict_passwords():
    """Passwords must be redacted in nested dicts."""
    data = {"email": "a@b.com", "password": "secret123"}
    result = redact_dict(data)
    assert result["email"] == "a@b.com"
    assert result["password"] == "[REDACTED]"


def test_redact_dict_nested():
    """Sensitive keys in nested structures must be redacted."""
    data = {"user": {"token": "abc123", "name": "Test"}}
    result = redact_dict(data)
    assert result["user"]["token"] == "[REDACTED]"
    assert result["user"]["name"] == "Test"


def test_redact_dict_lists():
    """Sensitive keys inside list items must be redacted."""
    data = [{"password": "x"}, {"email": "y"}]
    result = redact_dict(data)
    assert result[0]["password"] == "[REDACTED]"
    assert result[1]["email"] == "y"


def test_redact_all_sensitive_keys():
    """All documented sensitive keys should be redacted."""
    data = {
        "password": "x", "otp": "123456", "token": "jwt",
        "access_token": "at", "refresh_token": "rt",
        "authorization": "Bearer x", "hashed_password": "hash",
        "secret": "s", "api_key": "k", "app_key": "ak",
    }
    result = redact_dict(data)
    for key in data:
        assert result[key] == "[REDACTED]", f"Key '{key}' was not redacted"


def test_safe_parse_body_json():
    """JSON bodies should be parsed and redacted."""
    body = json.dumps({"password": "secret", "email": "a@b.com"}).encode()
    result = safe_parse_body(body)
    assert result["password"] == "[REDACTED]"
    assert result["email"] == "a@b.com"


def test_safe_parse_body_empty():
    """Empty body should return None."""
    assert safe_parse_body(b"") is None
    assert safe_parse_body(None) is None


def test_safe_parse_body_non_json():
    """Non-JSON body should return sentinel string."""
    assert safe_parse_body(b"\x00\x01\x02") == "[non-json body]"


def test_redact_query_params():
    """Token query params should be redacted."""
    params = {"page": "1", "token": "eyJhbG...", "access_token": "abc"}
    result = redact_query_params(params)
    assert result["page"] == "1"
    assert result["token"] == "[REDACTED]"
    assert result["access_token"] == "[REDACTED]"


# ─── Request ID Generator Tests ─────────────────────────────────────────────

def test_generate_request_id_default():
    """Without header, generates an 8-char UUID."""
    rid = generate_request_id()
    assert len(rid) == 8
    assert rid.replace("-", "").isalnum()


def test_generate_request_id_from_header():
    """With header, uses the sanitized header value."""
    rid = generate_request_id("my-trace-123")
    assert rid == "my-trace-123"


def test_generate_request_id_sanitizes():
    """Special characters in header are stripped."""
    rid = generate_request_id("inject<script>alert(1)")
    assert "<" not in rid
    assert ">" not in rid


# ─── Resource Monitor Tests ─────────────────────────────────────────────────

def test_resource_monitor_in_flight():
    """In-flight counter should increment and decrement correctly."""
    monitor = ResourceMonitor()
    assert monitor.in_flight == 0
    monitor.request_started()
    monitor.request_started()
    assert monitor.in_flight == 2
    monitor.request_finished()
    assert monitor.in_flight == 1
    monitor.request_finished()
    assert monitor.in_flight == 0


def test_resource_monitor_no_negative():
    """In-flight counter should never go below zero."""
    monitor = ResourceMonitor()
    monitor.request_finished()
    monitor.request_finished()
    assert monitor.in_flight == 0


def test_resource_snapshot_valid():
    """Snapshot should return a valid ResourceSnapshot."""
    monitor = ResourceMonitor()
    monitor.configure(enable_resource_tracking=True)
    snapshot = monitor.snapshot()
    assert isinstance(snapshot, ResourceSnapshot)
    assert snapshot.memory_rss_mb >= 0
    assert snapshot.cpu_percent >= 0
    assert snapshot.in_flight_requests == 0


def test_resource_monitor_disabled():
    """When disabled, snapshot should return zeroes for CPU/memory."""
    monitor = ResourceMonitor()
    monitor.configure(enable_resource_tracking=False)
    snapshot = monitor.snapshot()
    assert snapshot.memory_rss_mb == 0.0
    assert snapshot.cpu_percent == 0.0


# ─── Prometheus Metrics Endpoint Test ────────────────────────────────────────

@pytest.mark.asyncio(loop_scope="module")
async def test_metrics_endpoint_available(client):
    """/metrics should return Prometheus text format."""
    response = await client.get("/metrics")
    assert response.status_code == 200
    body = response.text
    # Should contain standard Prometheus metric names
    assert "http_requests_total" in body or "process_memory_rss_bytes" in body


@pytest.mark.asyncio(loop_scope="module")
async def test_metrics_no_app_key_required():
    """/metrics should work without X-App-Key header."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as bare_client:
        response = await bare_client.get("/metrics")
        # Should NOT be 401/403 even without X-App-Key
        assert response.status_code == 200


# ─── Health Check Still Works ────────────────────────────────────────────────

@pytest.mark.asyncio(loop_scope="module")
async def test_health_check(client):
    """Health check endpoint should still work with new middleware."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
