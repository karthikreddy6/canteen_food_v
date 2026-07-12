import asyncio
from datetime import datetime, timezone, date
from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sse_starlette.sse import EventSourceResponse

from typing import List
from app.database import get_db, AsyncSessionLocal
from app.models import User, MenuItem, Order, OrderItem, OrderStatus, CartItem, KitchenSettings, TimeSlot
from app.schemas import (
    CreateOrderRequest, OrderResponse, OrderItemResponse,
    UpdateOrderStatusRequest, OrderHistoryResponse, TimeSlotResponse
)
from app.security import get_current_user_id
from app.exceptions import NotFoundException, BadRequestException
from app.sse import sse_manager
from app.services.eta import calculate_eta, get_kitchen_settings, count_active_orders
from app.services.pickup import get_next_pickup_number

router = APIRouter(prefix="/api/orders", tags=["Orders"])


# ─── Helpers ───────────────────────────────────

def _build_order_response(order: Order) -> OrderResponse:
    items = []
    for oi in order.items:
        item_name = oi.menu_item.name if oi.menu_item else None
        items.append(OrderItemResponse(
            id=oi.id,
            order_id=oi.order_id,
            menu_item_id=oi.menu_item_id,
            item_name=item_name,
            quantity=oi.quantity,
            price_at_time_of_order=oi.price_at_time_of_order,
            line_total=Decimal(str(oi.price_at_time_of_order)) * oi.quantity,
        ))

    scheduled_slot_resp = None
    if order.scheduled_slot:
        from app.schemas import TimeSlotResponse
        scheduled_slot_resp = TimeSlotResponse(
            id=order.scheduled_slot.id,
            start_time=order.scheduled_slot.start_time,
            end_time=order.scheduled_slot.end_time,
            max_orders=order.scheduled_slot.max_orders,
            is_available=order.scheduled_slot.is_active
        )

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        total_amount=order.total_amount,
        status=order.status,
        pickup_number=order.pickup_number,
        pickup_date=order.pickup_date,
        estimated_ready_at=order.estimated_ready_at,
        actual_ready_at=order.actual_ready_at,
        notes=order.notes,
        created_at=order.created_at,
        items=items,
        scheduled_date=order.scheduled_date,
        scheduled_slot_id=order.scheduled_slot_id,
        scheduled_slot=scheduled_slot_resp
    )


async def _auto_progress_order(order_id: str):
    """
    Background task: auto-transitions PENDING → PREPARING after 60 seconds.
    Broadcasts the status change via SSE.
    """
    await asyncio.sleep(60)  # Wait 1 minute
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalars().first()
        if order and order.status == OrderStatus.PLACED:
            order.status = OrderStatus.PREPARING
            await db.commit()

            updated_at_str = datetime.now(timezone.utc).isoformat()
            if "." in updated_at_str:
                updated_at_str = updated_at_str.split(".")[0]

            await sse_manager.broadcast_to_user(order.user_id, "order-status", {
                "orderId": str(order.id),
                "userId": order.user_id,
                "status": OrderStatus.PREPARING.value,
                "pickupNumber": order.pickup_number,
                "estimatedReadyAt": order.estimated_ready_at.isoformat() if order.estimated_ready_at else None,
                "updatedAt": updated_at_str
            })


# ─── Endpoints ─────────────────────────────────

@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    request: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Place a new order.
    - Pulls items from cart if no items array provided.
    - Checks kitchen is accepting orders.
    - Validates availability of each item.
    - Validates total amount matches DB prices.
    - Auto-clears cart on success.
    - Assigns daily pickup number and ETA.
    - Starts background task to auto-progress status.
    """
    if request.user_id != current_user_id:
        raise BadRequestException("User ID mismatch with authenticated token")

    # 1. Verify user exists
    user_result = await db.execute(select(User).where(User.id == request.user_id))
    if not user_result.scalars().first():
        raise NotFoundException(f"User not found: {request.user_id}")

    # 2. Check kitchen is accepting orders
    settings = await get_kitchen_settings(db)
    if not settings.is_accepting_orders:
        raise BadRequestException("Kitchen is currently closed. Please try later.")
    active_count = await count_active_orders(db)
    if active_count >= settings.max_concurrent_orders:
        raise BadRequestException("Kitchen is at full capacity. Please try again in a few minutes.")

    # 3. Resolve items — from cart if not provided
    if request.items:
        item_requests = request.items
    else:
        cart_result = await db.execute(
            select(CartItem).where(CartItem.user_id == request.user_id)
        )
        cart_items = cart_result.scalars().all()
        if not cart_items:
            raise BadRequestException("Cart is empty. Add items before placing an order.")
        from app.schemas import CreateOrderItemRequest
        item_requests = [
            CreateOrderItemRequest(menu_item_id=ci.menu_item_id, quantity=ci.quantity)
            for ci in cart_items
        ]

    # 4. Validate each item's availability and calculate total
    calculated_total = Decimal("0.00")
    order_items = []
    menu_item_ids = []

    for item_req in item_requests:
        mi_result = await db.execute(
            select(MenuItem).where(MenuItem.id == item_req.menu_item_id)
        )
        menu_item = mi_result.scalars().first()
        if not menu_item:
            raise NotFoundException(f"Menu item not found: {item_req.menu_item_id}")
        if not menu_item.is_available:
            raise BadRequestException(
                f"'{menu_item.name}' is currently not available. "
                "Please remove it from your cart and try again."
            )

        item_price = Decimal(str(menu_item.price))
        calculated_total += item_price * item_req.quantity
        menu_item_ids.append(menu_item.id)

        order_items.append(OrderItem(
            menu_item_id=menu_item.id,
            quantity=item_req.quantity,
            price_at_time_of_order=menu_item.price
        ))

    # 5. Validate total amount
    client_total = request.total_amount.quantize(Decimal("0.01"))
    server_total = calculated_total.quantize(Decimal("0.01"))
    if client_total != server_total:
        raise BadRequestException(
            f"Order total does not match menu prices. "
            f"Expected: {server_total}, received: {client_total}"
        )

    # 6. Verify and handle Scheduling
    scheduled_dt = None
    order_status = OrderStatus.PLACED

    if (request.scheduled_date and not request.scheduled_slot_id) or (request.scheduled_slot_id and not request.scheduled_date):
        raise BadRequestException("Both scheduledDate and scheduledSlotId must be provided to schedule an order.")

    if request.scheduled_date and request.scheduled_slot_id:
        # Verify slot exists and is active
        slot_res = await db.execute(
            select(TimeSlot).where(
                TimeSlot.id == request.scheduled_slot_id,
                TimeSlot.is_active == True
            )
        )
        slot = slot_res.scalars().first()
        if not slot:
            raise NotFoundException(f"Time slot not found or inactive: {request.scheduled_slot_id}")

        # Verify date is in the future or today
        today = date.today()
        if request.scheduled_date < today:
            raise BadRequestException("Cannot schedule an order in the past.")

        # If date is today, verify start_time is in the future
        if request.scheduled_date == today:
            now_time = datetime.now().time()
            if slot.start_time <= now_time:
                raise BadRequestException("Cannot schedule an order for a past time slot today.")

        # Count existing orders booked for this slot on this date
        from sqlalchemy import func
        bookings_res = await db.execute(
            select(func.count(Order.id)).where(
                Order.scheduled_date == request.scheduled_date,
                Order.scheduled_slot_id == request.scheduled_slot_id,
                Order.status != OrderStatus.DELIVERED
            )
        )
        bookings_count = bookings_res.scalar() or 0
        if bookings_count >= slot.max_orders:
            raise BadRequestException(f"Time slot {slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')} is fully booked for {request.scheduled_date}")

        order_status = OrderStatus.SCHEDULED
        scheduled_dt = datetime.combine(request.scheduled_date, slot.end_time)
    else:
        # Calculate ETA (only for immediate orders)
        eta_data = await calculate_eta(db, menu_item_ids)
        scheduled_dt = eta_data["estimated_ready_at"]

    # 7. Get pickup number
    pickup_num, pickup_dt = await get_next_pickup_number(db)

    # 8. Create Order
    new_order = Order(
        user_id=request.user_id,
        total_amount=calculated_total,
        status=order_status,
        pickup_number=pickup_num,
        pickup_date=pickup_dt,
        estimated_ready_at=scheduled_dt,
        scheduled_date=request.scheduled_date,
        scheduled_slot_id=request.scheduled_slot_id,
        notes=request.notes,
        items=order_items
    )
    db.add(new_order)
    await db.flush()

    # 9. Auto-clear cart
    cart_result2 = await db.execute(
        select(CartItem).where(CartItem.user_id == request.user_id)
    )
    for ci in cart_result2.scalars().all():
        await db.delete(ci)

    await db.commit()

    # 10. Re-fetch with relationships
    result = await db.execute(select(Order).where(Order.id == new_order.id))
    saved_order = result.scalars().first()

    # 11. Fire-and-forget auto-progression background task (only for immediate orders)
    if saved_order.status == OrderStatus.PLACED:
        asyncio.create_task(_auto_progress_order(str(saved_order.id)))

    return _build_order_response(saved_order)


@router.get("/history", response_model=OrderHistoryResponse)
async def get_order_history(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Paginated order history for the logged-in user, newest first."""
    from sqlalchemy import func
    count_result = await db.execute(
        select(func.count(Order.id)).where(Order.user_id == current_user_id)
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(Order)
        .where(Order.user_id == current_user_id)
        .order_by(Order.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    orders = result.unique().scalars().all()

    return OrderHistoryResponse(
        orders=[_build_order_response(o) for o in orders],
        total=total,
        page=page,
        limit=limit
    )


@router.get("/{orderId}", response_model=OrderResponse)
async def get_order(
    orderId: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Retrieve a specific order by ID."""
    result = await db.execute(select(Order).where(Order.id == orderId))
    order = result.scalars().first()
    if not order:
        raise NotFoundException(f"Order not found: {orderId}")
    if order.user_id != current_user_id:
        raise BadRequestException("Access denied to view this order")
    return _build_order_response(order)


@router.patch("/{orderId}/status", response_model=OrderResponse)
async def update_order_status(
    orderId: UUID,
    request: UpdateOrderStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Update order status. When DELIVERED, records actual_ready_at."""
    result = await db.execute(select(Order).where(Order.id == orderId))
    order = result.scalars().first()
    if not order:
        raise NotFoundException(f"Order not found: {orderId}")

    order.status = request.status
    if request.status == OrderStatus.DELIVERED:
        order.actual_ready_at = datetime.now(timezone.utc)
    await db.commit()

    updated_at_str = datetime.now(timezone.utc).isoformat()
    if "." in updated_at_str:
        updated_at_str = updated_at_str.split(".")[0]

    await sse_manager.broadcast_to_user(order.user_id, "order-status", {
        "orderId": str(order.id),
        "userId": order.user_id,
        "status": order.status.value,
        "pickupNumber": order.pickup_number,
        "estimatedReadyAt": order.estimated_ready_at.isoformat() if order.estimated_ready_at else None,
        "updatedAt": updated_at_str
    })

    result = await db.execute(select(Order).where(Order.id == orderId))
    updated_order = result.scalars().first()
    return _build_order_response(updated_order)


@router.get("/stream/{userId}")
async def stream_order_status(
    userId: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Persistent SSE stream for real-time order tracking."""
    if userId != current_user_id:
        raise BadRequestException("User ID mismatch with authenticated token")

    async def event_generator():
        queue = await sse_manager.subscribe(userId)
        try:
            yield {"event": "connected", "data": "ok"}
            while True:
                event = await queue.get()
                yield event
        except asyncio.CancelledError:
            pass
        finally:
            sse_manager.unsubscribe(userId, queue)

    return EventSourceResponse(event_generator(), ping=120)


@router.get("/schedule/slots", response_model=List[TimeSlotResponse])
async def get_schedule_slots(
    date: date = Query(..., description="Date for scheduling (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all active time slots for the requested date, showing availability
    and bookings count.
    """
    from app.schemas import TimeSlotResponse
    
    # Fetch all active slots
    slots_res = await db.execute(
        select(TimeSlot).where(TimeSlot.is_active == True).order_by(TimeSlot.start_time)
    )
    slots = slots_res.scalars().all()

    # Fetch all bookings for this date (excluding DELIVERED)
    from sqlalchemy import func
    bookings_res = await db.execute(
        select(Order.scheduled_slot_id, func.count(Order.id))
        .where(Order.scheduled_date == date, Order.status != OrderStatus.DELIVERED)
        .group_by(Order.scheduled_slot_id)
    )
    bookings_map = {row[0]: row[1] for row in bookings_res.fetchall()}

    today = date.today()
    now_time = datetime.now().time()

    responses = []
    for slot in slots:
        booked = bookings_map.get(slot.id, 0)
        remaining = max(0, slot.max_orders - booked)

        # If date is today, check if start_time is in the past
        is_past = False
        if date == today and slot.start_time <= now_time:
            is_past = True

        responses.append(TimeSlotResponse(
            id=slot.id,
            start_time=slot.start_time,
            end_time=slot.end_time,
            max_orders=slot.max_orders,
            orders_booked=booked,
            orders_remaining=remaining,
            is_available=remaining > 0 and not is_past
        ))

    return responses
