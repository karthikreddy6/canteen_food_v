import hashlib
import uuid
from decimal import Decimal
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.future import select

from app.main import app
from app.database import AsyncSessionLocal, engine
from app.models import User, College, Canteen, MenuItem, Order, OrderItem, OrderStatus, SupportTicket, SupportMessage

CLIENT_HEADERS = {
    "X-App-Key": "ONFOOD_SECURE_CLIENT_APP_KEY_2026",
    "Content-Type": "application/json",
}


@pytest_asyncio.fixture(loop_scope="module")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        headers=CLIENT_HEADERS,
    ) as c:
        yield c
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="module")
async def auth_headers(client: AsyncClient):
    try:
        res = await client.post("/api/auth/login", json={
            "email": "karthik@example.com",
            "password": hashlib.sha256(b"karthik_password").hexdigest(),
        })
        if res.status_code == 200:
            data = res.json()
            return {
                **CLIENT_HEADERS,
                "Authorization": f"Bearer {data['accessToken']}",
            }
    except Exception:
        pass
    pytest.skip("Customer login failed; check database seed user.")


@pytest.mark.asyncio(loop_scope="module")
class TestUserProfileAvatarGender:
    async def test_update_profile_avatar_and_gender(self, client: AsyncClient, auth_headers: dict):
        res = await client.patch("/api/auth/profile", json={
            "avatar": "female",
            "gender": "FEMALE",
        }, headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert body["avatar"] == "female"
        assert body["gender"] == "FEMALE"
        assert body.get("hasChosenAvatar") is True

        # Update back to male
        res2 = await client.patch("/api/auth/profile", json={
            "avatar": "male",
            "gender": "MALE",
        }, headers=auth_headers)
        assert res2.status_code == 200
        body2 = res2.json()
        assert body2["avatar"] == "male"
        assert body2["gender"] == "MALE"
        assert body2.get("hasChosenAvatar") is True

        # Test GET /api/auth/profile
        res_get = await client.get("/api/auth/profile", headers=auth_headers)
        assert res_get.status_code == 200
        assert res_get.json()["avatar"] == "male"
        assert res_get.json().get("hasChosenAvatar") is True

        # Test DELETE /api/auth/device-token without auth (logout / token expired scenario)
        res_del = await client.request("DELETE", "/api/auth/device-token", json={
            "fcmToken": "dummy_test_fcm_token_123"
        }, headers=CLIENT_HEADERS)
        assert res_del.status_code == 200


@pytest.mark.asyncio(loop_scope="module")
class TestDynamicCartBilling:
    async def test_calculate_bill_with_items(self, client: AsyncClient, auth_headers: dict):
        # Fetch an available menu item
        async with AsyncSessionLocal() as db:
            item = (await db.execute(select(MenuItem).where(MenuItem.is_available == True))).scalars().first()
            assert item is not None, "No menu items in database"
            item_id = str(item.id)

        res = await client.post("/api/cart/calculate-bill", json={
            "items": [
                {"menuItemId": item_id, "quantity": 2}
            ]
        }, headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert "subtotal" in body
        assert "grandTotal" in body
        assert "breakdown" in body
        assert len(body["items"]) == 1
        assert body["items"][0]["quantity"] == 2

        titles = [b["title"] for b in body["breakdown"]]
        assert "Subtotal" in titles
        assert "Packaging Fee" in titles
        assert "GST (5%)" in titles


@pytest.mark.asyncio(loop_scope="module")
class TestCustomerSupportDesk:
    async def test_create_ticket_with_messages(self, client: AsyncClient, auth_headers: dict):
        # 1. Create a support ticket
        res = await client.post("/api/help/tickets", json={
            "subject": "Delayed Food Query",
            "message": "My order is delayed by 15 minutes, please assist."
        }, headers=auth_headers)
        assert res.status_code == 201
        ticket = res.json()
        assert "id" in ticket
        ticket_id = ticket["id"]
        assert ticket["subject"] == "Delayed Food Query"
        assert len(ticket.get("messages", [])) >= 1

        # 2. Get ticket messages
        msg_res = await client.get(f"/api/help/tickets/{ticket_id}/messages", headers=auth_headers)
        assert msg_res.status_code == 200
        messages = msg_res.json()
        assert len(messages) >= 1
        assert messages[0]["message"] == "My order is delayed by 15 minutes, please assist."

        # 3. Post a customer reply message
        post_res = await client.post(f"/api/help/tickets/{ticket_id}/messages", json={
            "message": "Nevermind, the canteen staff just handed me the packet!"
        }, headers=auth_headers)
        assert post_res.status_code == 201
        posted = post_res.json()
        assert posted["message"] == "Nevermind, the canteen staff just handed me the packet!"

        # 4. Resolve the ticket -> User receives "problem is resolved" notice
        resolve_res = await client.patch(f"/api/help/tickets/{ticket_id}/resolve", headers=auth_headers)
        assert resolve_res.status_code == 200
        resolved_data = resolve_res.json()
        assert resolved_data["status"] == "RESOLVED"

        resolved_msgs_res = await client.get(f"/api/help/tickets/{ticket_id}/messages", headers=auth_headers)
        resolved_msgs = resolved_msgs_res.json()
        assert any("marked as resolved" in m["message"] for m in resolved_msgs)

        # 5. User raises ticket again for the SAME order -> Continues old ticket and fires bot prompt
        reopen_res = await client.post("/api/help/tickets", json={
            "subject": "Still have an issue",
            "message": "Actually the packet was missing an item",
            "order_id": ticket.get("orderId") or "5c9229b3-d039-446f-9bc5-09c78d48b8d4"
        }, headers=auth_headers)
        assert reopen_res.status_code == 201
        reopened_data = reopen_res.json()
        # If orderId was present, it continues the same ticket
        reopened_msgs_res = await client.get(f"/api/help/tickets/{reopened_data['id']}/messages", headers=auth_headers)
        reopened_msgs = reopened_msgs_res.json()
        assert any("What seems to be the problem?" in m["message"] or "What is the problem" in m["message"] for m in reopened_msgs)


@pytest.mark.asyncio(loop_scope="module")
class TestOrderDelayAlertAndGeoDetails:
    async def test_order_details_include_canteen_and_college(self, client: AsyncClient, auth_headers: dict):
        async with AsyncSessionLocal() as db:
            order = (await db.execute(select(Order))).scalars().first()
            if not order:
                pytest.skip("No order present to test")
            order_id = str(order.id)

        res = await client.get(f"/api/orders/{order_id}", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "canteen" in data
        assert "college" in data

    async def test_kitchen_delay_alert_endpoint(self, client: AsyncClient, auth_headers: dict):
        async with AsyncSessionLocal() as db:
            order = (await db.execute(select(Order))).scalars().first()
            if not order:
                pytest.skip("No order present to test")
            order_id = str(order.id)

        res = await client.patch(f"/api/orders/{order_id}/delay", json={
            "minutes": 15,
            "message": "Rush in the kitchen! 15 minutes delay."
        }, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "delayed_notice_sent"
        assert data["extendedMinutes"] == 15


from unittest.mock import AsyncMock
from fastapi import WebSocketDisconnect
from app.main import websocket_support_endpoint
from app.security import create_access_token
import json


@pytest.mark.asyncio(loop_scope="module")
class TestSupportWebSocket:
    async def test_support_websocket_chat_and_bot_reply(self):
        try:
            async with AsyncSessionLocal() as db:
                user = (await db.execute(select(User))).scalars().first()
                if user is None:
                    pytest.skip("No user found in test database for WebSocket test")
                test_user_id = user.id
        except Exception:
            pytest.skip("Database not available for WebSocket test")

        token = create_access_token(test_user_id)
        sent_messages = []

        class MockWebSocket:
            def __init__(self):
                self.headers = {
                    "x-app-key": "ONFOOD_SECURE_CLIENT_APP_KEY_2026",
                    "user-agent": "automated-test",
                }
                self.query_params = {"token": token}
                self.client = type("MockClient", (), {"host": "127.0.0.1"})()
                self._calls = 0

            async def accept(self):
                pass

            async def receive_text(self):
                if self._calls == 0:
                    self._calls += 1
                    return json.dumps({
                        "type": "chat_message",
                        "message": "Hello support from automated async test!"
                    })
                raise WebSocketDisconnect(1000)

            async def send_text(self, text):
                sent_messages.append(text)

            async def close(self, code=1000, reason=""):
                pass

        mock_ws = MockWebSocket()
        await websocket_support_endpoint(mock_ws, test_user_id)

        assert len(sent_messages) == 1
        reply = json.loads(sent_messages[0])
        assert reply["type"] == "chat_message"
        assert reply["senderType"] == "BOT"
        assert "Buvva Assistant" in reply["senderName"]
        assert "Thanks for messaging!" in reply["message"]
