"""
Comprehensive server test suite for the OnFood backend.

Covers all major API endpoints across every router:
  - Health check
  - Auth (login, refresh, profile, logout)
  - Menu (list, paged, categories, sync, search, specials, discounts, by-category)
  - Cart (add, get, update, validate, bulk replace, delete item, clear)
  - Orders (place, history, detail, status update, schedule slots)
  - Kitchen (status, ETA preview)
  - Help & FAQ (list FAQ, get category, tickets)
  - Promotions (banners, coupon lookup, coupon apply)
  - Locations (colleges, canteens, college canteens)

Run:
    pytest tests/test_server.py -v
"""

import hashlib
import uuid
from datetime import date, timedelta

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# ─── Fixtures ──────────────────────────────────────────────────

CLIENT_HEADERS = {
    "X-App-Key": "ONFOOD_SECURE_CLIENT_APP_KEY_2026",
    "Content-Type": "application/json",
}


@pytest_asyncio.fixture(loop_scope="module")
async def client():
    """HTTPX AsyncClient wired to the FastAPI ASGI app."""
    from app.main import app
    from app.database import engine

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers=CLIENT_HEADERS,
    ) as c:
        yield c
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="module")
async def auth_headers(client: AsyncClient):
    """Log in as the seeded customer and return headers with Bearer token."""
    res = await client.post("/api/auth/login", json={
        "email": "karthik@example.com",
        "password": hashlib.sha256(b"karthik_password").hexdigest(),
    })
    if res.status_code != 200:
        pytest.skip("Customer login failed — ensure database is seeded.")
    data = res.json()
    return {
        **CLIENT_HEADERS,
        "Authorization": f"Bearer {data['accessToken']}",
        "_refresh_token": data["refreshToken"],
        "_user_id": data["user"]["id"],
    }


# ═══════════════════════════════════════════════════════════════
#  1. HEALTH CHECK
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio(loop_scope="module")
class TestHealthCheck:
    async def test_health_endpoint_returns_up(self, client):
        res = await client.get("/")
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "UP"
        assert "version" in body

    async def test_missing_app_key_rejected(self, client):
        """Request without X-App-Key should be rejected (401)."""
        from app.main import app
        from httpx import AsyncClient, ASGITransport

        # Use a separate client without default X-App-Key header
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as bare_client:
            res = await bare_client.get("/")
        assert res.status_code == 401


# ═══════════════════════════════════════════════════════════════
#  2. AUTHENTICATION
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio(loop_scope="module")
class TestAuth:
    async def test_login_success(self, client):
        res = await client.post("/api/auth/login", json={
            "email": "karthik@example.com",
            "password": hashlib.sha256(b"karthik_password").hexdigest(),
        })
        assert res.status_code == 200
        data = res.json()
        assert "accessToken" in data
        assert "refreshToken" in data
        assert data["user"]["email"] == "karthik@example.com"

    async def test_login_wrong_password(self, client):
        res = await client.post("/api/auth/login", json={
            "email": "karthik@example.com",
            "password": "wrong_password_hash",
        })
        assert res.status_code in (400, 401)

    async def test_login_nonexistent_user(self, client):
        res = await client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "doesnotmatter",
        })
        assert res.status_code in (400, 401, 404)

    async def test_refresh_token(self, client, auth_headers):
        refresh_token = auth_headers["_refresh_token"]
        res = await client.post("/api/auth/refresh", json={
            "refreshToken": refresh_token,
        })
        assert res.status_code == 200
        assert "accessToken" in res.json()

    async def test_profile_update(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        res = await client.patch("/api/auth/profile", headers=headers, json={
            "name": "Karthik",
        })
        assert res.status_code == 200
        assert res.json()["name"] == "Karthik"

    async def test_profile_without_auth_fails(self, client):
        res = await client.patch("/api/auth/profile", json={"name": "Hacker"})
        assert res.status_code == 401


# ═══════════════════════════════════════════════════════════════
#  3. MENU
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio(loop_scope="module")
class TestMenu:
    async def test_get_menu(self, client):
        res = await client.get("/api/menu")
        assert res.status_code == 200
        items = res.json()
        assert isinstance(items, list)
        if items:
            item = items[0]
            assert "id" in item
            assert "name" in item
            assert "price" in item
            assert "quantity" in item
            assert "isAvailable" in item

    async def test_get_menu_paged(self, client):
        res = await client.get("/api/menu/paged", params={"page": 1, "limit": 5})
        assert res.status_code == 200
        body = res.json()
        assert "items" in body
        assert "total" in body
        assert "hasMore" in body
        assert body["page"] == 1
        assert body["limit"] == 5

    async def test_get_categories(self, client):
        res = await client.get("/api/menu/categories")
        assert res.status_code == 200
        cats = res.json()
        assert isinstance(cats, list)
        if cats:
            assert "id" in cats[0]
            assert "name" in cats[0]

    async def test_get_menu_sync(self, client):
        res = await client.get("/api/menu/sync")
        assert res.status_code == 200
        body = res.json()
        assert "categories" in body
        assert "items" in body
        assert "serverTime" in body

    async def test_search_menu(self, client):
        res = await client.get("/api/menu/search", params={"q": "Biryani"})
        assert res.status_code == 200
        items = res.json()
        assert isinstance(items, list)
        # At least the seeded Chicken Biryani should match
        if items:
            assert any("biryani" in item["name"].lower() for item in items)

    async def test_search_empty_query_rejected(self, client):
        res = await client.get("/api/menu/search", params={"q": ""})
        assert res.status_code in (400, 422)  # server may coerce to 400

    async def test_get_specials(self, client):
        res = await client.get("/api/menu/specials")
        assert res.status_code == 200
        items = res.json()
        assert isinstance(items, list)

    async def test_get_discounts(self, client):
        res = await client.get("/api/menu/discounts")
        assert res.status_code == 200
        items = res.json()
        assert isinstance(items, list)

    async def test_get_items_by_category(self, client):
        # First get categories, then query by the first one
        cats_res = await client.get("/api/menu/categories")
        cats = cats_res.json()
        if not cats:
            pytest.skip("No categories found.")
        cat_id = cats[0]["id"]
        res = await client.get(f"/api/menu/category/{cat_id}")
        assert res.status_code == 200
        assert isinstance(res.json(), list)


# ═══════════════════════════════════════════════════════════════
#  4. CART
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio(loop_scope="module")
class TestCart:
    async def test_clear_cart(self, client, auth_headers):
        """Start clean."""
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        res = await client.delete("/api/cart", headers=headers)
        assert res.status_code == 204

    async def test_get_empty_cart(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        res = await client.get("/api/cart", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert body["totalItems"] == 0
        assert body["items"] == []

    async def test_add_item_to_cart(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        # Get a menu item to add
        menu_res = await client.get("/api/menu")
        items = menu_res.json()
        if not items:
            pytest.skip("No menu items available.")
        item = items[0]

        res = await client.post("/api/cart/items", headers=headers, json={
            "menuItemId": item["id"],
            "quantity": 2,
        })
        assert res.status_code == 201
        body = res.json()
        assert body["menuItemId"] == item["id"]
        assert body["quantity"] == 2

    async def test_get_cart_with_items(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        res = await client.get("/api/cart", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert body["totalItems"] >= 1
        assert len(body["items"]) >= 1

    async def test_update_cart_item_quantity(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        # Get cart to find the item ID
        cart_res = await client.get("/api/cart", headers=headers)
        cart_items = cart_res.json()["items"]
        if not cart_items:
            pytest.skip("Cart is empty.")
        cart_item_id = cart_items[0]["id"]

        res = await client.patch(
            f"/api/cart/items/{cart_item_id}",
            headers=headers,
            json={"quantity": 3},
        )
        assert res.status_code == 200
        assert res.json()["quantity"] == 3

    async def test_validate_cart(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        res = await client.post("/api/cart/validate", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert "isValid" in body
        assert "currentTotal" in body

    async def test_bulk_replace_cart(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        menu_res = await client.get("/api/menu")
        items = menu_res.json()
        if len(items) < 2:
            pytest.skip("Need at least 2 menu items for bulk replace test.")

        # Pick two items from the same canteen
        canteen_id = items[0].get("canteenId")
        same_canteen = [i for i in items if i.get("canteenId") == canteen_id]
        if len(same_canteen) < 2:
            pytest.skip("Need 2+ items from same canteen.")

        res = await client.put("/api/cart", headers=headers, json={
            "items": [
                {"menuItemId": same_canteen[0]["id"], "quantity": 1},
                {"menuItemId": same_canteen[1]["id"], "quantity": 2},
            ]
        })
        assert res.status_code == 200
        body = res.json()
        assert body["totalItems"] >= 2

    async def test_delete_single_cart_item(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        cart_res = await client.get("/api/cart", headers=headers)
        cart_items = cart_res.json()["items"]
        if not cart_items:
            pytest.skip("Cart is empty.")
        item_id = cart_items[0]["id"]
        res = await client.delete(f"/api/cart/items/{item_id}", headers=headers)
        assert res.status_code == 204

    async def test_cart_without_auth_fails(self, client):
        res = await client.get("/api/cart")
        assert res.status_code == 401


# ═══════════════════════════════════════════════════════════════
#  5. ORDERS
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio(loop_scope="module")
class TestOrders:
    async def test_place_order(self, client, auth_headers):
        """Place a real order from the cart."""
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}

        # Clear and rebuild cart with 1 item
        await client.delete("/api/cart", headers=headers)
        menu_res = await client.get("/api/menu")
        items = menu_res.json()
        if not items:
            pytest.skip("No menu items to place an order.")
        item = items[0]

        await client.post("/api/cart/items", headers=headers, json={
            "menuItemId": item["id"],
            "quantity": 1,
        })

        # Validate cart to get the correct total
        validate_res = await client.post("/api/cart/validate", headers=headers)
        total = validate_res.json()["currentTotal"]

        res = await client.post("/api/orders", headers=headers, json={
            "totalAmount": float(total),
            "notes": "Test order from pytest",
        })
        assert res.status_code == 201
        order = res.json()
        assert "id" in order
        assert order["status"] == "placed"
        assert order["pickupNumber"] is not None

        # Stash the order ID for subsequent tests
        TestOrders._order_id = order["id"]

    async def test_order_history(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        res = await client.get("/api/orders/history", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert "orders" in body
        assert body["total"] >= 1

    async def test_get_order_detail(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        order_id = getattr(TestOrders, "_order_id", None)
        if not order_id:
            pytest.skip("No order was placed in earlier test.")
        res = await client.get(f"/api/orders/{order_id}", headers=headers)
        assert res.status_code == 200
        assert res.json()["id"] == order_id

    async def test_get_nonexistent_order(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        fake_id = str(uuid.uuid4())
        res = await client.get(f"/api/orders/{fake_id}", headers=headers)
        assert res.status_code == 404

    async def test_cancel_order(self, client, auth_headers):
        """Customer can cancel their own order."""
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        order_id = getattr(TestOrders, "_order_id", None)
        if not order_id:
            pytest.skip("No order to cancel.")
        res = await client.patch(
            f"/api/orders/{order_id}/status",
            headers=headers,
            json={"status": "cancelled"},
        )
        # Should succeed or fail with a known business reason
        assert res.status_code in (200, 400)

    async def test_price_tampering_rejected(self, client, auth_headers):
        """Server must reject orders where totalAmount doesn't match cart total."""
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        await client.delete("/api/cart", headers=headers)
        menu_res = await client.get("/api/menu")
        items = menu_res.json()
        if not items:
            pytest.skip("No menu items.")
        await client.post("/api/cart/items", headers=headers, json={
            "menuItemId": items[0]["id"],
            "quantity": 1,
        })
        res = await client.post("/api/orders", headers=headers, json={
            "totalAmount": 0.01,  # tampered price
            "notes": "Security test",
        })
        assert res.status_code == 400

    async def test_past_date_scheduling_blocked(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        past_date = (date.today() - timedelta(days=1)).isoformat()
        res = await client.post("/api/orders", headers=headers, json={
            "totalAmount": 10.0,
            "scheduledDate": past_date,
            "scheduledSlotId": "00000000-0000-0000-0000-000000000001",
        })
        assert res.status_code == 400

    async def test_schedule_slots(self, client):
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        res = await client.get("/api/orders/schedule/slots", params={"date": tomorrow})
        assert res.status_code == 200
        slots = res.json()
        assert isinstance(slots, list)

    async def test_stream_ticket_requires_auth(self, client):
        res = await client.post("/api/orders/stream/ticket")
        assert res.status_code == 401

    async def test_stream_ticket_success(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        res = await client.post("/api/orders/stream/ticket", headers=headers)
        assert res.status_code == 201
        body = res.json()
        assert "ticket" in body
        assert body["expiresInSeconds"] == 30

    async def test_orders_without_auth_fails(self, client):
        res = await client.get("/api/orders/history")
        assert res.status_code == 401


# ═══════════════════════════════════════════════════════════════
#  6. KITCHEN
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio(loop_scope="module")
class TestKitchen:
    async def test_kitchen_status(self, client):
        res = await client.get("/api/kitchen/status")
        assert res.status_code == 200
        body = res.json()
        assert "isAcceptingOrders" in body
        assert "estimatedWaitMinutes" in body
        assert "activeOrdersCount" in body

    async def test_eta_preview(self, client):
        menu_res = await client.get("/api/menu")
        items = menu_res.json()
        if not items:
            pytest.skip("No menu items for ETA preview.")
        res = await client.post("/api/kitchen/eta", json={
            "items": [{"menuItemId": items[0]["id"], "quantity": 1}],
        })
        assert res.status_code == 200
        body = res.json()
        assert "estimatedReadyMinutes" in body
        assert "estimatedReadyAt" in body

    async def test_eta_with_empty_items(self, client):
        res = await client.post("/api/kitchen/eta", json={"items": []})
        assert res.status_code in (200, 400, 422)


# ═══════════════════════════════════════════════════════════════
#  7. HELP & FAQ
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio(loop_scope="module")
class TestHelp:
    async def test_get_faq_list(self, client):
        res = await client.get("/api/help/faq")
        assert res.status_code == 200
        categories = res.json()
        assert isinstance(categories, list)
        if categories:
            cat = categories[0]
            assert "title" in cat
            assert "items" in cat

    async def test_get_faq_category(self, client):
        faq_res = await client.get("/api/help/faq")
        cats = faq_res.json()
        if not cats:
            pytest.skip("No FAQ categories.")
        cat_id = cats[0]["id"]
        res = await client.get(f"/api/help/faq/{cat_id}")
        assert res.status_code == 200
        assert res.json()["id"] == cat_id

    async def test_get_faq_nonexistent_category(self, client):
        fake_id = str(uuid.uuid4())
        res = await client.get(f"/api/help/faq/{fake_id}")
        assert res.status_code == 404

    async def test_create_ticket(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        res = await client.post("/api/help/tickets", headers=headers, json={
            "subject": "Test ticket from pytest",
            "message": "This is an automated test ticket. Please ignore.",
        })
        assert res.status_code == 201
        body = res.json()
        assert body["subject"] == "Test ticket from pytest"
        assert body["status"] == "open"
        TestHelp._ticket_id = body["id"]

    async def test_list_tickets(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        res = await client.get("/api/help/tickets", headers=headers)
        assert res.status_code == 200
        tickets = res.json()
        assert isinstance(tickets, list)
        assert len(tickets) >= 1

    async def test_get_ticket_detail(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        ticket_id = getattr(TestHelp, "_ticket_id", None)
        if not ticket_id:
            pytest.skip("No ticket was created.")
        res = await client.get(f"/api/help/tickets/{ticket_id}", headers=headers)
        assert res.status_code == 200
        assert res.json()["id"] == ticket_id

    async def test_tickets_without_auth(self, client):
        res = await client.get("/api/help/tickets")
        assert res.status_code == 401


# ═══════════════════════════════════════════════════════════════
#  8. PROMOTIONS (Banners & Coupons)
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio(loop_scope="module")
class TestPromotions:
    async def test_get_banners(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        res = await client.get("/api/banners", headers=headers)
        assert res.status_code == 200
        banners = res.json()
        assert isinstance(banners, list)

    async def test_get_banners_without_auth_fails(self, client):
        res = await client.get("/api/banners")
        assert res.status_code == 401

    async def test_lookup_nonexistent_coupon(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        res = await client.get("/api/coupons/FAKECODE999", headers=headers)
        assert res.status_code in (400, 404)

    async def test_apply_coupon_invalid_code(self, client, auth_headers):
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        menu_res = await client.get("/api/menu")
        items = menu_res.json()
        if not items:
            pytest.skip("No menu items.")
        res = await client.post("/api/coupons/apply", headers=headers, json={
            "couponCode": "INVALID_CODE",
            "items": [{"menuItemId": items[0]["id"], "quantity": 1}],
        })
        assert res.status_code in (400, 404)

    async def test_vendor_endpoints_require_vendor_auth(self, client, auth_headers):
        """Customer JWT must not access vendor-only endpoints."""
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        res = await client.get("/api/vendor/coupons", headers=headers)
        assert res.status_code == 401

        res = await client.get("/api/vendor/banners", headers=headers)
        assert res.status_code == 401


# ═══════════════════════════════════════════════════════════════
#  9. LOCATIONS
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio(loop_scope="module")
class TestLocations:
    async def test_list_colleges(self, client):
        res = await client.get("/api/locations/colleges")
        assert res.status_code == 200
        colleges = res.json()
        assert isinstance(colleges, list)
        assert len(colleges) >= 1
        TestLocations._college_id = colleges[0]["id"]

    async def test_list_canteens(self, client):
        res = await client.get("/api/locations/canteens")
        assert res.status_code == 200
        canteens = res.json()
        assert isinstance(canteens, list)
        assert len(canteens) >= 1

    async def test_list_canteens_by_college(self, client):
        college_id = getattr(TestLocations, "_college_id", None)
        if not college_id:
            pytest.skip("No college ID available.")
        res = await client.get(f"/api/locations/colleges/{college_id}/canteens")
        assert res.status_code == 200
        canteens = res.json()
        assert isinstance(canteens, list)

    async def test_list_canteens_filtered_by_query_param(self, client):
        college_id = getattr(TestLocations, "_college_id", None)
        if not college_id:
            pytest.skip("No college ID available.")
        res = await client.get("/api/locations/canteens", params={"collegeId": college_id})
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    async def test_suggest_college(self, client):
        res = await client.post("/api/locations/colleges/suggest", json={
            "name": "Pytest Test College",
        })
        assert res.status_code == 201

    async def test_nonexistent_college_canteens(self, client):
        fake_id = str(uuid.uuid4())
        res = await client.get(f"/api/locations/colleges/{fake_id}/canteens")
        # Should return empty list or 404
        assert res.status_code in (200, 404)


# ═══════════════════════════════════════════════════════════════
#  10. SECURITY EDGE CASES
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio(loop_scope="module")
class TestSecurityEdgeCases:
    async def test_expired_token_rejected(self, client):
        """A fabricated expired token should be rejected."""
        headers = {
            **CLIENT_HEADERS,
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxMDAwMDAwMDAwfQ.invalid",
        }
        res = await client.get("/api/cart", headers=headers)
        assert res.status_code == 401

    async def test_malformed_token_rejected(self, client):
        headers = {**CLIENT_HEADERS, "Authorization": "Bearer not.a.valid.jwt"}
        res = await client.get("/api/cart", headers=headers)
        assert res.status_code == 401

    async def test_customer_cannot_update_to_completed(self, client, auth_headers):
        """A customer should not be able to mark any order as COMPLETED."""
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        fake_id = "00000000-0000-0000-0000-000000000000"
        res = await client.patch(
            f"/api/orders/{fake_id}/status",
            headers=headers,
            json={"status": "completed"},
        )
        # Should be 400 (unauthorized transition), 403, or 404 (order not found)
        assert res.status_code in (400, 403, 404)

    async def test_register_missing_fields(self, client):
        """Registration with missing required fields should fail."""
        res = await client.post("/api/auth/register", json={
            "email": "incomplete@test.com",
        })
        assert res.status_code in (400, 422)  # server may coerce to 400

    async def test_extra_fields_rejected(self, client, auth_headers):
        """CamelRequestModel has extra='forbid', so unknown fields should cause 422."""
        headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
        res = await client.post("/api/cart/items", headers=headers, json={
            "menuItemId": str(uuid.uuid4()),
            "quantity": 1,
            "hackerField": "should be rejected",
        })
        assert res.status_code == 422
