import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings

TEST_KEY = "ONFOOD_SECURE_CLIENT_APP_KEY_2026"


@pytest.fixture(autouse=True)
def ensure_app_client_key():
    """Ensure settings.APP_CLIENT_KEY is configured for static security tests."""
    original_key = settings.APP_CLIENT_KEY
    settings.APP_CLIENT_KEY = TEST_KEY
    yield
    settings.APP_CLIENT_KEY = original_key


@pytest.mark.asyncio
async def test_static_icons_without_key_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get("/icons/biryani.png")
        assert res.status_code == 401
        data = res.json()
        assert data["status"] == 401
        assert data["error"] == "Unauthorized"
        assert "app client key" in data["message"].lower()


@pytest.mark.asyncio
async def test_static_images_without_key_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get("/images/chicken-biryani.png")
        assert res.status_code == 401
        data = res.json()
        assert data["status"] == 401
        assert data["error"] == "Unauthorized"


@pytest.mark.asyncio
async def test_static_sounds_without_key_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get("/sounds/bell.wav")
        assert res.status_code == 401
        data = res.json()
        assert data["status"] == 401
        assert data["error"] == "Unauthorized"


@pytest.mark.asyncio
async def test_static_icons_with_header_success():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"X-App-Key": TEST_KEY},
    ) as client:
        res = await client.get("/icons/biryani.png")
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("image/png")
        assert len(res.content) > 0


@pytest.mark.asyncio
async def test_static_images_with_header_success():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"X-App-Key": TEST_KEY},
    ) as client:
        res = await client.get("/images/chicken-biryani.png")
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("image/png")
        assert len(res.content) > 0


@pytest.mark.asyncio
async def test_static_sounds_with_header_success():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"X-App-Key": TEST_KEY},
    ) as client:
        res = await client.get("/sounds/bell.wav")
        assert res.status_code == 200
        assert "wav" in res.headers["content-type"]
        assert len(res.content) > 0


@pytest.mark.asyncio
async def test_static_icons_with_query_param_key():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get(f"/icons/biryani.png?key={TEST_KEY}")
        assert res.status_code == 200
        assert len(res.content) > 0


@pytest.mark.asyncio
async def test_static_images_with_query_param_app_key():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get(f"/images/chicken-biryani.png?app_key={TEST_KEY}")
        assert res.status_code == 200
        assert len(res.content) > 0


@pytest.mark.asyncio
async def test_static_sounds_with_query_param_x_app_key():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get(f"/sounds/bell.wav?x-app-key={TEST_KEY}")
        assert res.status_code == 200
        assert len(res.content) > 0


@pytest.mark.asyncio
async def test_static_with_invalid_header_key_rejected():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"X-App-Key": "INVALID_KEY_123"},
    ) as client:
        res = await client.get("/icons/biryani.png")
        assert res.status_code == 401
        assert res.json()["status"] == 401


@pytest.mark.asyncio
async def test_static_with_invalid_query_param_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get("/sounds/bell.wav?key=INVALID_KEY_123")
        assert res.status_code == 401
        assert res.json()["status"] == 401


@pytest.mark.asyncio
async def test_static_nonexistent_file_without_key_returns_401():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.get("/images/nonexistent_secret.png")
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_static_nonexistent_file_with_valid_key_returns_404():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers={"X-App-Key": TEST_KEY},
    ) as client:
        res = await client.get("/images/nonexistent_secret.png")
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_static_dev_mode_without_configured_key_allows_access():
    settings.APP_CLIENT_KEY = None
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            res = await client.get("/icons/biryani.png")
            assert res.status_code == 200
    finally:
        settings.APP_CLIENT_KEY = TEST_KEY
