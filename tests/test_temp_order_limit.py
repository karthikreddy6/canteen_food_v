from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import uuid

from app.exceptions import BadRequestException
from app.routers.orders import (
    create_order,
    TEMP_ORDER_MAX_AMOUNT,
    TEMP_ORDER_COOLDOWN_SECONDS,
    TEMP_ORDER_RULES_ENABLED,
)
from app.schemas import CreateOrderRequest, CreateOrderItemRequest
from app.models import User, MenuItem, KitchenSettings, OrderStatus


def _create_mock_order(user_id, canteen_id, total_amount=Decimal("200.00")):
    saved_order = MagicMock()
    saved_order.id = uuid.uuid4()
    saved_order.user_id = user_id
    saved_order.status = OrderStatus.DELIVERED
    saved_order.total_amount = total_amount
    saved_order.discount_amount = Decimal("0.00")
    saved_order.coupon_code = None
    saved_order.pickup_number = 1
    saved_order.pickup_date = datetime.now().date()
    saved_order.estimated_ready_at = None
    saved_order.actual_ready_at = None
    saved_order.notes = None
    saved_order.created_at = datetime.now()
    saved_order.items = []
    saved_order.scheduled_date = None
    saved_order.scheduled_slot_id = None
    saved_order.scheduled_slot = None
    saved_order.points_earned = 0
    saved_order.user_roll_number = None
    saved_order.order_token = "1"
    saved_order.canteen_id = canteen_id
    saved_order.user = MagicMock()
    return saved_order


@pytest.mark.asyncio
async def test_create_order_cooldown_blocks_within_3_hours():
    """Verify that a user who ordered 1 hour ago is blocked by the 3-hour cooldown."""
    db = AsyncMock()
    user_id = "test-user-id"

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    user = User(
        id=user_id,
        name="Test User",
        email="test@example.com",
        phone="919876543210",
        last_order_at=now - timedelta(hours=1),  # Ordered 1 hour ago
        status="active",
        is_premium=False,
        use_roll_number_as_order_token=False,
        reward_points_balance=0,
        lifetime_points_earned=0,
    )
    user_scalar = MagicMock()
    user_scalar.first.return_value = user
    user_res = MagicMock()
    user_res.scalars.return_value = user_scalar

    db.execute.return_value = user_res

    req = CreateOrderRequest(
        items=[CreateOrderItemRequest(menu_item_id=uuid.uuid4(), quantity=1)],
        total_amount=Decimal("150.00"),
    )

    with pytest.raises(BadRequestException) as exc_info:
        await create_order(request=req, db=db, current_user_id=user_id)

    assert "Order cooldown in effect" in exc_info.value.message
    assert "3 hours" in exc_info.value.message
    assert "hour" in exc_info.value.message


@pytest.mark.asyncio
async def test_create_order_cooldown_allows_after_3_hours():
    """Verify that a user who ordered 3.5 hours ago is allowed to place an order."""
    db = AsyncMock()
    user_id = "test-user-id"

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    user = User(
        id=user_id,
        name="Test User",
        email="test@example.com",
        phone="919876543210",
        last_order_at=now - timedelta(hours=3, minutes=30),  # Ordered 3.5 hours ago
        status="active",
        is_premium=False,
        use_roll_number_as_order_token=False,
        reward_points_balance=0,
        lifetime_points_earned=0,
        preferred_canteen_id=None,
    )
    settings = KitchenSettings(
        is_accepting_orders=True,
        max_concurrent_orders=50,
        base_prep_buffer_minutes=2,
    )
    item_id = uuid.uuid4()
    canteen_id = uuid.uuid4()
    item = MenuItem(
        id=item_id,
        canteen_id=canteen_id,
        name="Thali",
        price=Decimal("200.00"),
        stock=10,
        is_available=True,
        preparation_time_minutes=15,
    )

    user_scalar = MagicMock()
    user_scalar.first.return_value = user
    user_res = MagicMock()
    user_res.scalars.return_value = user_scalar

    menu_scalar = MagicMock()
    menu_scalar.all.return_value = [item]
    menu_res = MagicMock()
    menu_res.scalars.return_value = menu_scalar

    cart_scalar = MagicMock()
    cart_scalar.all.return_value = []
    cart_res = MagicMock()
    cart_res.scalars.return_value = cart_scalar

    db.execute.side_effect = [user_res, menu_res, cart_res]
    db.flush = AsyncMock()
    db.commit = AsyncMock()

    req = CreateOrderRequest(
        items=[CreateOrderItemRequest(menu_item_id=item_id, quantity=1)],
        total_amount=Decimal("200.00"),
    )

    saved_order = _create_mock_order(user_id, canteen_id, Decimal("200.00"))

    with patch("app.routers.orders.get_kitchen_settings", AsyncMock(return_value=settings)), \
         patch("app.routers.orders.count_active_orders", AsyncMock(return_value=0)), \
         patch("app.routers.orders.get_next_pickup_number", AsyncMock(return_value=(1, datetime.now().date()))), \
         patch("app.routers.orders._load_order_for_response", AsyncMock(return_value=saved_order)), \
         patch("app.routers.orders.sse_manager.broadcast_to_user", AsyncMock()), \
         patch("app.pubsub.event_bridge.notify", AsyncMock()):
        
        response = await create_order(request=req, db=db, current_user_id=user_id)
        assert response.total_amount == Decimal("200.00")


@pytest.mark.asyncio
async def test_create_order_rejects_above_250():
    """Verify that an order with total > ₹250 is rejected."""
    db = AsyncMock()
    user_id = "test-user-id"

    user = User(
        id=user_id,
        name="Test User",
        email="test@example.com",
        phone="919876543210",
        last_order_at=None,
        status="active",
        is_premium=False,
        use_roll_number_as_order_token=False,
        reward_points_balance=0,
        lifetime_points_earned=0,
    )
    settings = KitchenSettings(
        is_accepting_orders=True,
        max_concurrent_orders=50,
        base_prep_buffer_minutes=2,
    )
    item_id = uuid.uuid4()
    canteen_id = uuid.uuid4()
    item = MenuItem(
        id=item_id,
        canteen_id=canteen_id,
        name="Special Feast",
        price=Decimal("260.00"),
        stock=10,
        is_available=True,
        preparation_time_minutes=15,
    )

    user_scalar = MagicMock()
    user_scalar.first.return_value = user
    user_res = MagicMock()
    user_res.scalars.return_value = user_scalar

    menu_scalar = MagicMock()
    menu_scalar.all.return_value = [item]
    menu_res = MagicMock()
    menu_res.scalars.return_value = menu_scalar

    db.execute.side_effect = [user_res, menu_res]

    req = CreateOrderRequest(
        items=[CreateOrderItemRequest(menu_item_id=item_id, quantity=1)],
        total_amount=Decimal("260.00"),
    )

    with patch("app.routers.orders.get_kitchen_settings", AsyncMock(return_value=settings)), \
         patch("app.routers.orders.count_active_orders", AsyncMock(return_value=0)):
        
        with pytest.raises(BadRequestException) as exc_info:
            await create_order(request=req, db=db, current_user_id=user_id)

        assert "Temporary order limit" in exc_info.value.message
        assert "250.00" in exc_info.value.message
        assert "blocked" in exc_info.value.message


@pytest.mark.asyncio
async def test_create_order_allows_250():
    """Verify that an order with total exactly ₹250 succeeds."""
    db = AsyncMock()
    user_id = "test-user-id"

    user = User(
        id=user_id,
        name="Test User",
        email="test@example.com",
        phone="919876543210",
        last_order_at=None,
        status="active",
        is_premium=False,
        use_roll_number_as_order_token=False,
        reward_points_balance=0,
        lifetime_points_earned=0,
        preferred_canteen_id=None,
    )
    settings = KitchenSettings(
        is_accepting_orders=True,
        max_concurrent_orders=50,
        base_prep_buffer_minutes=2,
    )
    item_id = uuid.uuid4()
    canteen_id = uuid.uuid4()
    item = MenuItem(
        id=item_id,
        canteen_id=canteen_id,
        name="Combo Meal",
        price=Decimal("250.00"),
        stock=10,
        is_available=True,
        preparation_time_minutes=15,
    )

    user_scalar = MagicMock()
    user_scalar.first.return_value = user
    user_res = MagicMock()
    user_res.scalars.return_value = user_scalar

    menu_scalar = MagicMock()
    menu_scalar.all.return_value = [item]
    menu_res = MagicMock()
    menu_res.scalars.return_value = menu_scalar

    cart_scalar = MagicMock()
    cart_scalar.all.return_value = []
    cart_res = MagicMock()
    cart_res.scalars.return_value = cart_scalar

    db.execute.side_effect = [user_res, menu_res, cart_res]
    db.flush = AsyncMock()
    db.commit = AsyncMock()

    req = CreateOrderRequest(
        items=[CreateOrderItemRequest(menu_item_id=item_id, quantity=1)],
        total_amount=Decimal("250.00"),
    )

    saved_order = _create_mock_order(user_id, canteen_id, Decimal("250.00"))

    with patch("app.routers.orders.get_kitchen_settings", AsyncMock(return_value=settings)), \
         patch("app.routers.orders.count_active_orders", AsyncMock(return_value=0)), \
         patch("app.routers.orders.get_next_pickup_number", AsyncMock(return_value=(1, datetime.now().date()))), \
         patch("app.routers.orders._load_order_for_response", AsyncMock(return_value=saved_order)), \
         patch("app.routers.orders.sse_manager.broadcast_to_user", AsyncMock()), \
         patch("app.pubsub.event_bridge.notify", AsyncMock()):
        
        response = await create_order(request=req, db=db, current_user_id=user_id)
        assert response.total_amount == Decimal("250.00")
