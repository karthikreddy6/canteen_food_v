import asyncio
import re
from datetime import datetime, timezone, date, timedelta
from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sse_starlette.sse import EventSourceResponse

from typing import List, Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_db, AsyncSessionLocal
from app.models import Canteen, User, MenuItem, Order, OrderItem, OrderStatus, CartItem, KitchenSettings, TimeSlot, Coupon
from app.config import settings as app_settings
from app.schemas import (
    CreateOrderRequest, OrderResponse, OrderItemResponse,
    UpdateOrderStatusRequest, OrderHistoryResponse, TimeSlotResponse,
    StreamTicketResponse,
)
from app.security import get_current_user_id, get_current_user_id_verified, get_current_user_id_optional
from app.exceptions import NotFoundException, BadRequestException
from app.sse import sse_manager
from app.services.eta import get_kitchen_settings, count_active_orders
from app.services.pickup import get_next_pickup_number

router = APIRouter(prefix="/api/orders", tags=["Orders"])


def order_json(order: Order) -> dict:
    items_summary = ", ".join(
        f"{item.menu_item.name if item.menu_item else item.menu_item_id} x {item.quantity}"
        for item in order.items
    )
    student_name = order.user.name if order.user else "Student"
    placed_time = order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else None
    return {
        "id": str(order.id),
        "userId": order.user_id,
        "canteenId": str(order.canteen_id) if order.canteen_id else None,
        "status": order.status.value,
        "totalAmount": float(order.total_amount),
        "pickupNumber": order.pickup_number,
        "token": order.order_token or (str(order.pickup_number) if order.pickup_number is not None else str(order.id)[:8]),
        "studentName": student_name,
        "student_name": student_name,
        "rollNo": order.user_roll_number or "",
        "roll_no": order.user_roll_number or "",
        "branch": order.user.college if order.user and order.user.college else "",
        "itemsSummary": items_summary,
        "items_summary": items_summary,
        "total_amount": float(order.total_amount),
        "placed_time": placed_time,
        "scheduledDate": order.scheduled_date.isoformat() if order.scheduled_date else None,
        "scheduledSlotId": str(order.scheduled_slot_id) if order.scheduled_slot_id else None,
        "notes": order.notes,
        "createdAt": order.created_at.isoformat() if order.created_at else None,
        "items": [
            {
                "menuItemId": str(item.menu_item_id),
                "name": item.menu_item.name if item.menu_item else None,
                "quantity": item.quantity,
                "price": str(item.price_at_time_of_order)
            }
            for item in order.items
        ]
    }


def _roll_number_token(roll_number: str | None, fallback: int) -> str:
    """Return the final three numeric characters of a roll number."""
    digits = re.sub(r"\D", "", roll_number or "")
    return digits[-3:] if digits else str(fallback)


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
        canteen_id=order.canteen_id,
        user_roll_number=order.user_roll_number,
        order_token=order.order_token or (str(order.pickup_number) if order.pickup_number is not None else str(order.id)[:8]),
        total_amount=order.total_amount,
        discount_amount=order.discount_amount or Decimal("0.00"),
        coupon_code=order.coupon_code,
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


async def _load_order_for_response(db: AsyncSession, order_id: UUID) -> Order | None:
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.menu_item),
            selectinload(Order.user),
            selectinload(Order.scheduled_slot),
        )
        .where(Order.id == order_id)
    )
    return result.unique().scalars().first()


async def _auto_progress_order(order_id: str):
    """
    Background task: auto-transitions PENDING → PREPARING after 60 seconds.
    Broadcasts the status change via SSE.
    """
    await asyncio.sleep(60)  # Wait 1 minute
    async with AsyncSessionLocal() as db:
        order = await _load_order_for_response(db, UUID(order_id))
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

            # Cross-notify vendor (real-time sync)
            try:
                from app.pubsub import event_bridge
                payload = order_json(order)
                await event_bridge.notify("order_status_updated", payload)
            except Exception as e:
                print(f"[SSE Error] Failed to broadcast auto-progression to vendor: {e}")


# ─── Endpoints ─────────────────────────────────

@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    request: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id_verified)
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
    # user_id comes exclusively from the JWT — never from the request body
    user_id = current_user_id

    # 1. Verify user exists
    user_result = await db.execute(
        select(User).where(User.id == user_id).with_for_update()
    )
    user = user_result.scalars().first()
    if not user:
        raise NotFoundException(f"User not found: {user_id}")

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if user.last_order_at:
        last_order_at = user.last_order_at.replace(tzinfo=None)
        elapsed = (now - last_order_at).total_seconds()
        if elapsed < app_settings.ORDER_COOLDOWN_SECONDS:
            remaining = max(1, int(app_settings.ORDER_COOLDOWN_SECONDS - elapsed))
            raise BadRequestException(
                f"Please wait {remaining} seconds before placing another order."
            )

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
            select(CartItem).where(CartItem.user_id == user_id)
        )
        cart_items = cart_result.scalars().all()
        if not cart_items:
            raise BadRequestException("Cart is empty. Add items before placing an order.")
        from app.schemas import CreateOrderItemRequest
        item_requests = [
            CreateOrderItemRequest(menu_item_id=ci.menu_item_id, quantity=ci.quantity)
            for ci in cart_items
        ]

    # 4. Validate item availability and calculate total in one menu query
    calculated_total = Decimal("0.00")
    order_items = []
    requested_item_ids = [item_req.menu_item_id for item_req in item_requests]
    menu_result = await db.execute(
        select(MenuItem).where(MenuItem.id.in_(requested_item_ids)).with_for_update()
    )
    menu_items_by_id = {item.id: item for item in menu_result.scalars().all()}

    missing_ids = [item_id for item_id in requested_item_ids if item_id not in menu_items_by_id]
    if missing_ids:
        raise NotFoundException(f"Menu item not found: {missing_ids[0]}")

    prep_times = []
    canteen_ids = set()
    for item_req in item_requests:
        menu_item = menu_items_by_id[item_req.menu_item_id]
        canteen_ids.add(menu_item.canteen_id)
        if not menu_item.is_available:
            raise BadRequestException(
                f"'{menu_item.name}' is currently not available. "
                "Please remove it from your cart and try again."
            )

        # Validate stock quantity
        if menu_item.stock < item_req.quantity:
            raise BadRequestException(
                f"Insufficient stock for '{menu_item.name}'. "
                f"Available: {menu_item.stock}, requested: {item_req.quantity}."
            )

        # Decrement stock
        menu_item.stock -= item_req.quantity

        item_price = Decimal(str(menu_item.price))
        calculated_total += item_price * item_req.quantity
        prep_times.append(menu_item.preparation_time_minutes)

        order_items.append(OrderItem(
            menu_item_id=menu_item.id,
            quantity=item_req.quantity,
            price_at_time_of_order=menu_item.price
        ))

    # Validate all items belong to ONE canteen (ignore None/unassigned items)
    real_canteen_ids = {cid for cid in canteen_ids if cid is not None}
    if len(real_canteen_ids) > 1:
        raise BadRequestException("An order can only contain items from one canteen at a time.")
    # Auto-assign canteen: from items if set, otherwise from user's preferred canteen
    order_canteen_id = real_canteen_ids.pop() if real_canteen_ids else user.preferred_canteen_id

    # 5. Apply and validate coupon
    discount_amount = Decimal("0.00")
    coupon = None
    coupon_code = request.coupon_code.strip().upper() if request.coupon_code else None
    if coupon_code:
        from app.models import CouponUsage
        from sqlalchemy import func as sqlfunc

        coupon_result = await db.execute(
            select(Coupon).where(Coupon.code == coupon_code).with_for_update()
        )
        coupon = coupon_result.scalars().first()

        if not coupon or not coupon.active:
            raise BadRequestException("Coupon is invalid or inactive.")
        if coupon.expires_at and coupon.expires_at.replace(tzinfo=None) <= now:
            raise BadRequestException("Coupon has expired.")
        if coupon.max_uses is not None and coupon.used_count >= coupon.max_uses:
            raise BadRequestException("Coupon usage limit has been reached.")

        # Check minimum order amount
        if coupon.min_order_amount is not None and calculated_total < Decimal(str(coupon.min_order_amount)):
            raise BadRequestException(
                f"This coupon requires a minimum order of ₹{coupon.min_order_amount}. "
                f"Your cart total is ₹{calculated_total}."
            )

        # Check per-user usage limit
        if coupon.per_user_limit is not None:
            usage_count_res = await db.execute(
                select(sqlfunc.count(CouponUsage.id)).where(
                    CouponUsage.coupon_id == coupon.id,
                    CouponUsage.user_id == user_id
                )
            )
            user_usage_count = usage_count_res.scalar() or 0
            if user_usage_count >= coupon.per_user_limit:
                raise BadRequestException(
                    "You have already used this coupon the maximum number of times."
                )

        # Calculate discount
        if coupon.discount_type.upper() == "PERCENT":
            if coupon.value < 0 or coupon.value > 100:
                raise BadRequestException("Coupon percentage is invalid.")
            discount_amount = calculated_total * coupon.value / Decimal("100")
        else:
            discount_amount = min(calculated_total, Decimal(str(coupon.value)))

        # Apply max discount cap
        if coupon.max_discount_amount is not None:
            discount_amount = min(discount_amount, Decimal(str(coupon.max_discount_amount)))

        discount_amount = discount_amount.quantize(Decimal("0.01"))

    final_total = calculated_total - discount_amount

    # 6. Validate total amount
    client_total = request.total_amount.quantize(Decimal("0.01"))
    server_total = final_total.quantize(Decimal("0.01"))
    if client_total != server_total:
        raise BadRequestException(
            f"Order total does not match menu prices. "
            f"Expected: {server_total}, received: {client_total}"
        )

    # 7. Verify and handle Scheduling
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

        # If date is today, verify start_time is at least 1 hour in the future
        if request.scheduled_date == today:
            lead_time_cutoff = (datetime.now() + timedelta(hours=1)).time()
            if slot.start_time < lead_time_cutoff:
                raise BadRequestException("Scheduled orders must be placed at least 1 hour in advance.")

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
        base_prep = max(prep_times) if prep_times else 10
        queue_buffer = max(0, active_count) * settings.base_prep_buffer_minutes
        scheduled_dt = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
            minutes=base_prep + queue_buffer
        )

    # 8. Get pickup number
    pickup_num, pickup_dt = await get_next_pickup_number(db)

    # 9. Create Order
    new_order = Order(
        user_id=user_id,
        canteen_id=order_canteen_id,
        user_roll_number=user.roll_number,
        total_amount=final_total,
        discount_amount=discount_amount,
        coupon_code=coupon_code,
        status=order_status,
        pickup_number=pickup_num,
        pickup_date=pickup_dt,
        order_token=(_roll_number_token(user.roll_number, pickup_num)
                     if user.use_roll_number_as_order_token and user.roll_number
                     else str(pickup_num)),
        estimated_ready_at=scheduled_dt,
        scheduled_date=request.scheduled_date,
        scheduled_slot_id=request.scheduled_slot_id,
        notes=request.notes,
        items=order_items
    )
    user.last_order_at = now
    if coupon:
        coupon.used_count += 1
        from app.models import CouponUsage
        db.add(CouponUsage(coupon_id=coupon.id, user_id=user_id))
    db.add(new_order)
    await db.flush()

    # 10. Auto-clear cart
    cart_result2 = await db.execute(
        select(CartItem).where(CartItem.user_id == user_id)
    )
    for ci in cart_result2.scalars().all():
        await db.delete(ci)

    await db.commit()

    # 11. Re-fetch with relationships
    saved_order = await _load_order_for_response(db, new_order.id)

    # 11b. Cross-broadcast new order to vendor app screens (real-time sync)
    try:
        from app.pubsub import event_bridge
        payload = order_json(saved_order)
        await event_bridge.notify("order_created", payload)
    except Exception as e:
        print(f"[SSE Error] Failed to broadcast new order to vendor: {e}")

    # 12. Auto-accept is controlled per canteen. When disabled (the default),
    # the order stays PLACED until the vendor accepts it.
    if saved_order.status == OrderStatus.PLACED:
        canteen = (await db.execute(select(Canteen).where(Canteen.id == order_canteen_id))).scalar_one_or_none()
        if canteen and canteen.auto_accept_orders:
            saved_order.status = OrderStatus.PREPARING
            await db.commit()
            await db.refresh(saved_order)
            await sse_manager.broadcast_to_user(saved_order.user_id, "order-status", {
                "orderId": str(saved_order.id), "userId": saved_order.user_id,
                "status": OrderStatus.PREPARING.value, "pickupNumber": saved_order.pickup_number,
                "estimatedReadyAt": saved_order.estimated_ready_at.isoformat() if saved_order.estimated_ready_at else None,
                "updatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            })
            try:
                from app.pubsub import event_bridge
                await event_bridge.notify("order_status_updated", order_json(saved_order))
            except Exception as e:
                print(f"[SSE Error] Failed to broadcast canteen auto-acceptance to vendor: {e}")

    return _build_order_response(saved_order)


@router.get("/history", response_model=OrderHistoryResponse)
async def get_order_history(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id_verified)
):
    """Paginated order history for the logged-in user, newest first."""
    from sqlalchemy import func
    count_result = await db.execute(
        select(func.count(Order.id)).where(Order.user_id == current_user_id)
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.menu_item),
            selectinload(Order.scheduled_slot),
        )
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
    current_user_id: str = Depends(get_current_user_id_verified)
):
    """Retrieve a specific order by ID."""
    order = await _load_order_for_response(db, orderId)
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
    current_user_id: str = Depends(get_current_user_id_verified)
):
    """Update order status. Only the order's owner (customer) may call this endpoint."""
    order = await _load_order_for_response(db, orderId)
    if not order:
        raise NotFoundException(f"Order not found: {orderId}")

    # Ownership enforcement: only the customer who placed this order may update its status.
    # Vendor-initiated status changes will use dedicated vendor endpoints in the future.
    if order.user_id != current_user_id:
        from app.exceptions import BadRequestException
        raise BadRequestException("You are not authorised to update this order")

    # If transitioning to a cancelled/rejected state from an active state, restore stock
    is_cancelling = request.status in {OrderStatus.REJECTED, OrderStatus.CANCELLED}
    was_cancelled = order.status in {OrderStatus.REJECTED, OrderStatus.CANCELLED}
    if is_cancelling and not was_cancelled:
        for oi in order.items:
            if oi.menu_item:
                oi.menu_item.stock += oi.quantity

    order.status = request.status
    if request.status == OrderStatus.DELIVERED:
        order.actual_ready_at = datetime.now(timezone.utc)

    # Construct the payload before commit to avoid any session expiration / lazy loading issues
    try:
        payload = order_json(order)
    except Exception as e:
        print(f"[SSE Error] Failed to serialize order payload: {e}")
        payload = None

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

    # Cross-notify vendor (real-time sync)
    if payload:
        try:
            from app.pubsub import event_bridge
            await event_bridge.notify("order_status_updated", payload)
        except Exception as e:
            print(f"[SSE Error] Failed to broadcast status update to vendor: {e}")

    updated_order = await _load_order_for_response(db, orderId)
    return _build_order_response(updated_order)


@router.post("/stream/ticket", response_model=StreamTicketResponse, status_code=201)
async def create_stream_ticket(
    current_user_id: str = Depends(get_current_user_id_verified),
):
    """
    Issue a single-use, 30-second SSE/WebSocket auth ticket.
    Call this right before opening the stream connection, then pass
    ?ticket=<token> instead of the raw JWT in the URL.
    The ticket is deleted from Redis on first use.
    """
    import secrets as _secrets
    ticket = _secrets.token_urlsafe(32)
    ticket_key = f"onfood:sse_ticket:{ticket}"

    from app.config import settings as _cfg
    if _cfg.CACHE_REDIS_URL:
        try:
            import redis.asyncio as aioredis
            r = aioredis.from_url(_cfg.CACHE_REDIS_URL, decode_responses=True)
            await r.set(ticket_key, current_user_id, ex=30)  # 30-second TTL
            await r.aclose()
        except Exception as e:
            # Fall back to a signed short-lived JWT when Redis is unavailable
            from app.security import create_access_token
            print(f"[SSE Ticket] Redis unavailable, falling back to JWT: {e}")
            ticket = create_access_token(current_user_id, token_version=1)
    else:
        # No Redis: use a short-lived JWT as the ticket (development only)
        from app.security import create_access_token
        ticket = create_access_token(current_user_id, token_version=1)

    return StreamTicketResponse(ticket=ticket, expires_in_seconds=30)
@router.get("/stream/{userId}")
async def stream_order_status(
    userId: str,
    request: Request,
    ticket: str = Query(None, description="One-time SSE ticket from POST /stream/ticket (preferred)"),
    token: str = Query(None, description="JWT token fallback (leaks to proxy logs — prefer ticket)"),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
):
    """
    SSE stream for real-time order status tracking.

    Auth options (one is required, in priority order):
      1. One-time ticket: ?ticket=<token>  (preferred — get from POST /stream/ticket)
      2. Header:          Authorization: Bearer <token>   (standard fallback)
      3. Query param JWT: ?token=<token>   (last resort — leaks to proxy logs)
    """
    from app.config import settings as _cfg
    import jwt as pyjwt

    current_user_id: str | None = None

    # ── Priority 1: One-time Redis ticket ──
    ticket = request.query_params.get("ticket")
    if ticket:
        if _cfg.CACHE_REDIS_URL:
            try:
                import redis.asyncio as aioredis
                r = aioredis.from_url(_cfg.CACHE_REDIS_URL, decode_responses=True)
                stored_user_id = await r.get(f"onfood:sse_ticket:{ticket}")
                if stored_user_id:
                    await r.delete(f"onfood:sse_ticket:{ticket}")  # single-use
                    current_user_id = stored_user_id
                await r.aclose()
            except Exception as e:
                print(f"[SSE Auth] Redis error during ticket validation: {e}")
        else:
            # No Redis — treat ticket as a short-lived JWT (dev fallback)
            try:
                from app.security import settings as _sec_settings
                p = pyjwt.decode(ticket, _sec_settings.JWT_SECRET, algorithms=["HS256"], issuer=_sec_settings.JWT_ISSUER)
                current_user_id = str(p.get("sub", "")) or None
            except Exception:
                pass

    # ── Priority 2/3: JWT (header or query param) ──
    if not current_user_id:
        raw_token = None
        if credentials:
            raw_token = credentials.credentials
        elif token:
            raw_token = token

        if raw_token:
            try:
                from app.security import settings as _sec_settings
                payload = pyjwt.decode(raw_token, _sec_settings.JWT_SECRET, algorithms=["HS256"], issuer=_sec_settings.JWT_ISSUER)
                if payload.get("type") == "access":
                    current_user_id = str(payload.get("sub", "")) or None
            except pyjwt.ExpiredSignatureError:
                raise BadRequestException("Token has expired")
            except pyjwt.InvalidTokenError as e:
                raise BadRequestException(f"Invalid token: {e}")

    if not current_user_id:
        raise BadRequestException("Authentication required. Use ?ticket= (preferred) or Authorization header.")

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
    canteen_id: Optional[str] = Query(None, alias="canteenId"),
    db: AsyncSession = Depends(get_db),
    current_user_id: Optional[str] = Depends(get_current_user_id_optional)
):
    """
    Get all active time slots for the requested date and canteen, showing
    availability and bookings count.  Each canteen has its own named breaks
    (Breakfast, Lunch, Snacks, Dinner …).
    If canteenId is omitted, resolves from the user's preferred_canteen_id.
    """
    from app.schemas import TimeSlotResponse
    from sqlalchemy import func, or_

    # ── Resolve canteen ──
    cid = _parse_optional_uuid(canteen_id)
    if cid is None and current_user_id:
        user = (await db.execute(
            select(User).where(User.id == current_user_id)
        )).scalar_one_or_none()
        if user and user.preferred_canteen_id:
            cid = user.preferred_canteen_id

    # ── Fetch active slots for the canteen (+ global fallback) ──
    if cid:
        canteen_check = (await db.execute(
            select(Canteen).where(Canteen.id == cid, Canteen.is_active == True)
        )).scalar_one_or_none()
        if not canteen_check:
            return []  # Inactive canteen -> return no time slots

    slot_filter = [TimeSlot.is_active == True]
    if cid:
        slot_filter.append(
            or_(TimeSlot.canteen_id == cid, TimeSlot.canteen_id == None)
        )

    slots_res = await db.execute(
        select(TimeSlot).where(*slot_filter).order_by(TimeSlot.start_time)
    )
    slots = slots_res.scalars().all()

    # ── Bookings count for the date (excluding DELIVERED) ──
    bookings_res = await db.execute(
        select(Order.scheduled_slot_id, func.count(Order.id))
        .where(Order.scheduled_date == date, Order.status != OrderStatus.DELIVERED)
        .group_by(Order.scheduled_slot_id)
    )
    bookings_map = {row[0]: row[1] for row in bookings_res.fetchall()}

    today = date.today()
    lead_time_cutoff = (datetime.now() + timedelta(hours=1)).time()

    responses = []
    for slot in slots:
        booked = bookings_map.get(slot.id, 0)
        remaining = max(0, slot.max_orders - booked)

        # Require at least 1 hour lead time for today's orders
        is_too_soon = (date == today and slot.start_time < lead_time_cutoff)

        # Format user-friendly label if null or empty (e.g. "08:00 AM - 08:30 AM")
        display_label = slot.label
        if not display_label or not display_label.strip():
            start_str = datetime.combine(date.today(), slot.start_time).strftime("%I:%M %p")
            end_str = datetime.combine(date.today(), slot.end_time).strftime("%I:%M %p")
            display_label = f"{start_str} - {end_str}"

        responses.append(TimeSlotResponse(
            id=slot.id,
            canteen_id=slot.canteen_id,
            label=display_label,
            start_time=slot.start_time,
            end_time=slot.end_time,
            max_orders=slot.max_orders,
            orders_booked=booked,
            orders_remaining=remaining,
            is_available=remaining > 0 and not is_too_soon
        ))

    return responses


# ── Helper ──────────────────────────────────────
def _parse_optional_uuid(val: Optional[str]) -> Optional[UUID]:
    """Safely parse a string to UUID, returning None for empty / invalid."""
    if not val or not val.strip():
        return None
    try:
        return UUID(val.strip())
    except ValueError:
        return None
