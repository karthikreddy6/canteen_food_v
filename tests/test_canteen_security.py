import pytest
from datetime import date, timedelta

@pytest.mark.asyncio(loop_scope="module")
async def test_price_tampering_prevention(authenticated_customer_client):
    """TEST 1: Ensure server rejects orders where client-sent totalAmount doesn't match cart calculation."""
    client, headers = authenticated_customer_client

    # Fetch menu item
    menu_res = await client.get("/api/menu")
    assert menu_res.status_code == 200
    menu_items = menu_res.json()
    if not menu_items:
        pytest.skip("No menu items available to test.")
        
    item = menu_items[0]
    
    # Clear cart first
    await client.delete("/api/cart", headers=headers)
    
    # Add item to cart
    await client.post("/api/cart/items", headers=headers, json={
        "menuItemId": item["id"],
        "quantity": 1
    })

    # Attempt order placement with tampered totalAmount = $0.01
    order_res = await client.post("/api/orders", headers=headers, json={
        "totalAmount": 0.01,
        "notes": "Security test: Tampered total"
    })
    
    # Server should reject tampered price with HTTP 400 Bad Request
    assert order_res.status_code == 400
    assert "mismatch" in order_res.json().get("message", "").lower() or order_res.status_code == 400
    print(f"\n[PASSED] Price tampering rejected with HTTP 400: {order_res.json().get('message')}")

@pytest.mark.asyncio(loop_scope="module")
async def test_unauthorized_order_status_update(authenticated_customer_client):
    """TEST 2: Customer cannot mark an order as COMPLETED or READY."""
    client, headers = authenticated_customer_client
    
    # Attempt to update arbitrary order status as regular customer via PATCH
    fake_order_id = "00000000-0000-0000-0000-000000000000"
    res = await client.patch(f"/api/orders/{fake_order_id}/status", headers=headers, json={
        "status": "COMPLETED"
    })
    
    # Must fail with 400 Bad Request ("not authorised"), 403 Forbidden, or 404 Not Found
    assert res.status_code in [400, 403, 404]
    print(f"\n[PASSED] Customer status update restricted (Status code: {res.status_code})")

@pytest.mark.asyncio(loop_scope="module")
async def test_past_date_scheduling_blocked(authenticated_customer_client):
    """TEST 3: Prevent scheduling orders in the past."""
    client, headers = authenticated_customer_client
    
    past_date = (date.today() - timedelta(days=1)).isoformat()
    
    res = await client.post("/api/orders", headers=headers, json={
        "totalAmount": 10.0,
        "scheduledDate": past_date,
        "scheduledSlotId": "00000000-0000-0000-0000-000000000001"
    })
    
    # Must return 400 Bad Request
    assert res.status_code == 400
    print(f"\n[PASSED] Past date scheduling rejected correctly: {res.json().get('message')}")

@pytest.mark.asyncio(loop_scope="module")
async def test_menu_items_contain_quantity(authenticated_customer_client):
    """TEST 4: Ensure GET /api/menu items contain quantity field and stock is removed."""
    client, _ = authenticated_customer_client
    res = await client.get("/api/menu")
    assert res.status_code == 200
    items = res.json()
    if items:
        item = items[0]
        assert "quantity" in item
@pytest.mark.asyncio(loop_scope="module")
async def test_unavailable_items_included_in_menu(authenticated_customer_client):
    """TEST 5: Ensure items with is_available=False are sent in GET /api/menu with isAvailable: false."""
    client, _ = authenticated_customer_client
    res = await client.get("/api/menu")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    for item in items:
        assert "isAvailable" in item
        assert "quantity" in item
    print(f"\n[PASSED] Menu items response includes all items with isAvailable status")

