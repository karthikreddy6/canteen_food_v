import asyncio
import os
from datetime import date, timedelta
from httpx import AsyncClient, ASGITransport

# Disable order cooldown during testing
os.environ["ORDER_COOLDOWN_SECONDS"] = "0"

import pytest
from app.main import app

@pytest.mark.asyncio(loop_scope="module")
async def test_order_scheduling():
    client_headers = {"X-App-Key": "ONFOOD_SECURE_CLIENT_APP_KEY_2026"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=client_headers) as c:
        import hashlib
        login_res = await c.post("/api/auth/login", json={
            "email": "karthik@example.com",
            "password": hashlib.sha256(b"karthik_password").hexdigest()
        })
        login_data = login_res.json()
        token = login_data["accessToken"]
        user_id = login_data["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Determine target date: tomorrow
        target_date = (date.today() + timedelta(days=1)).isoformat()
        print(f"Target date for scheduled orders: {target_date}")
        
        # 2. Get slots
        print(f"\n1. Fetching available time slots for {target_date}...")
        slots_res = await c.get(f"/api/orders/schedule/slots?date={target_date}")
        assert slots_res.status_code == 200
        slots = slots_res.json()
        print(f"Fetched {len(slots)} slots successfully.")
        
        # Pick the first slot
        slot = slots[0]
        slot_id = slot["id"]
        print(f"Selected time slot: {slot['startTime']} - {slot['endTime']} (Max: {slot['maxOrders']}, Booked: {slot['ordersBooked']})")
        
        # Clear cart first to start fresh
        await c.delete("/api/cart", headers=headers)
        
        # Get menu items
        menu_res = await c.get("/api/menu")
        pizza = next(i for i in menu_res.json() if "Biryani" in i["name"])
        
        # 3. Book the slot up to limit
        max_capacity = slot["maxOrders"]
        print(f"\n2. Booking slot {slot['startTime']} up to its limit of {max_capacity} orders...")
        
        order_ids = []
        for i in range(max_capacity):
            # Re-add item to cart because cart auto-clears on order success
            await c.post("/api/cart/items", headers=headers, json={"menuItemId": pizza["id"], "quantity": 1})
            
            res = await c.post("/api/orders", headers=headers, json={
                "totalAmount": float(pizza["price"]),
                "scheduledDate": target_date,
                "scheduledSlotId": slot_id
            })
            if res.status_code == 201:
                order_data = res.json()
                order_ids.append(order_data["id"])
                print(f" -> Order {i+1} placed. ID: {order_data['id']} (Status: {order_data['status']}, Pickup#: {order_data['pickupNumber']})")
            else:
                print(f" -> Order {i+1} failed: {res.status_code} - {res.text}")
                assert False
                
        # 4. Attempt to place 6th order in same slot (exceeding limit of 5)
        print("\n3. Attempting to place a 6th order exceeding slot capacity (Limit: 5)...")
        # Add item to cart
        await c.post("/api/cart/items", headers=headers, json={"menuItemId": pizza["id"], "quantity": 1})
        
        failed_res = await c.post("/api/orders", headers=headers, json={
            "totalAmount": float(pizza["price"]),
            "scheduledDate": target_date,
            "scheduledSlotId": slot_id
        })
        print(f" -> Result Status Code: {failed_res.status_code}")
        print(f" -> Error Message: {failed_res.json()['message']}")
        assert failed_res.status_code == 400
        assert "fully booked" in failed_res.json()["message"]
        print(" -> SUCCESS: Exceeding booking limit rejected correctly!")
        
        # 5. Verify time slots endpoint now shows slot is booked
        print("\n4. Verifying slots endpoint reflects booking status...")
        slots_res_after = await c.get(f"/api/orders/schedule/slots?date={target_date}")
        slots_after = slots_res_after.json()
        slot_after = next(s for s in slots_after if s["id"] == slot_id)
        print(f" -> Slot after bookings: Booked: {slot_after['ordersBooked']}, Remaining: {slot_after['ordersRemaining']}, Available: {slot_after['isAvailable']}")
        assert slot_after["ordersBooked"] == max_capacity
        assert slot_after["ordersRemaining"] == 0
        assert slot_after["isAvailable"] is False
        print(" -> SUCCESS: Slot marked fully booked!")

        print("\n=== ALL SCHEDULING TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    asyncio.run(test_order_scheduling())
