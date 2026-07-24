import sys
import os
import hashlib
from pathlib import Path
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Disable order cooldown during automated testing
os.environ["ORDER_COOLDOWN_SECONDS"] = "0"

from app.main import app
from app.database import engine

CLIENT_HEADERS = {
    "X-App-Key": "ONFOOD_SECURE_CLIENT_APP_KEY_2026",
    "Content-Type": "application/json"
}

@pytest_asyncio.fixture(loop_scope="module")
async def async_client():
    """Provides an HTTPX AsyncClient bound to the FastAPI application."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers=CLIENT_HEADERS
    ) as client:
        yield client
    await engine.dispose()

@pytest_asyncio.fixture(loop_scope="module")
async def authenticated_customer_client(async_client):
    """Logs in as a regular customer and returns headers with Bearer token."""
    login_res = await async_client.post("/api/auth/login", json={
        "email": "karthik@example.com",
        "password": hashlib.sha256(b"karthik_password").hexdigest()
    })
    
    if login_res.status_code == 200:
        token = login_res.json()["accessToken"]
        auth_headers = {
            **CLIENT_HEADERS,
            "Authorization": f"Bearer {token}"
        }
        return async_client, auth_headers
    else:
        pytest.skip("Customer login failed; check database seed user.")
