from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import CartItem, MenuItem, User, Coupon
from app.schemas import (
    CartResponse, CartItemResponse, AddToCartRequest, BulkReplaceCartRequest,
    UpdateCartItemRequest, CartValidateResponse, CartValidateIssue,
    CalculateBillRequest, BillResponse, BillItemDetail, BreakdownItem
)
from app.security import get_current_user_id_verified as get_current_user_id
from app.exceptions import NotFoundException, BadRequestException
from app.college_scoping import get_user_college_info

router = APIRouter(prefix="/api/cart", tags=["Cart"])


# ─── Helpers ───────────────────────────────────

def _build_cart_item_response(cart_item: CartItem) -> CartItemResponse:
    item = cart_item.menu_item
    line_total = Decimal(str(item.price)) * cart_item.quantity
    return CartItemResponse(
        id=cart_item.id,
        menu_item_id=cart_item.menu_item_id,
        canteen_id=cart_item.canteen_id or item.canteen_id,
        quantity=cart_item.quantity,
        item_name=item.name,
        item_price=item.price,
        item_original_price=item.original_price,
        item_discount_percent=item.discount_percent,
        item_image_url=item.image_url,
        item_is_available=item.is_available,
        line_total=line_total,
    )


# ─── Endpoints ─────────────────────────────────

@router.get("", response_model=CartResponse)
async def get_cart(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get the current user's cart with item details and subtotal."""
    result = await db.execute(
        select(CartItem).where(CartItem.user_id == user_id)
    )
    cart_items = result.scalars().all()

    items_response = [_build_cart_item_response(ci) for ci in cart_items]
    subtotal = sum(i.line_total for i in items_response)

    return CartResponse(
        items=items_response,
        subtotal=subtotal,
        total_items=sum(i.quantity for i in items_response)
    )


@router.post("/items", response_model=CartItemResponse, status_code=201)
async def add_to_cart(
    request: AddToCartRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Add a menu item to cart. If already in cart, increments quantity."""
    menu_result = await db.execute(
        select(MenuItem).where(MenuItem.id == request.menu_item_id)
    )
    menu_item = menu_result.scalars().first()
    if not menu_item:
        raise NotFoundException(f"Menu item not found: {request.menu_item_id}")
    if not menu_item.is_available:
        raise BadRequestException(f"'{menu_item.name}' is currently not available")

    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    has_college, _, allowed_canteen_ids, _ = await get_user_college_info(db, user)
    if has_college and (not allowed_canteen_ids or menu_item.canteen_id not in allowed_canteen_ids):
        raise BadRequestException("You can only add items from your college canteens to your cart")

    existing_canteens = await db.execute(select(CartItem.canteen_id).where(CartItem.user_id == user_id).limit(1))
    existing_canteen = existing_canteens.scalar_one_or_none()
    if existing_canteen and existing_canteen != menu_item.canteen_id:
        raise BadRequestException("Your cart can contain items from only one canteen")

    # Check if already in cart
    existing_result = await db.execute(
        select(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.menu_item_id == request.menu_item_id
        )
    )
    existing = existing_result.scalars().first()

    if existing:
        existing.quantity += request.quantity
        cart_item_id = existing.id
    else:
        cart_item = CartItem(
            user_id=user_id,
            menu_item_id=request.menu_item_id,
            canteen_id=menu_item.canteen_id,
            quantity=request.quantity
        )
        db.add(cart_item)
        await db.flush()
        cart_item_id = cart_item.id

    await db.commit()

    # Re-fetch with joined menu_item
    refreshed = await db.execute(select(CartItem).where(CartItem.id == cart_item_id))
    saved = refreshed.scalars().first()
    return _build_cart_item_response(saved)


@router.patch("/items/{cart_item_id}", response_model=CartItemResponse)
async def update_cart_item(
    cart_item_id: str,
    request: UpdateCartItemRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Update quantity of a cart item."""
    result = await db.execute(
        select(CartItem).where(
            CartItem.id == cart_item_id,
            CartItem.user_id == user_id
        )
    )
    cart_item = result.scalars().first()
    if not cart_item:
        raise NotFoundException(f"Cart item not found: {cart_item_id}")

    cart_item.quantity = request.quantity
    await db.commit()

    refreshed = await db.execute(select(CartItem).where(CartItem.id == cart_item_id))
    saved = refreshed.scalars().first()
    return _build_cart_item_response(saved)


@router.delete("/items/{cart_item_id}", status_code=204)
async def remove_cart_item(
    cart_item_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Remove a single item from the cart."""
    result = await db.execute(
        select(CartItem).where(
            CartItem.id == cart_item_id,
            CartItem.user_id == user_id
        )
    )
    cart_item = result.scalars().first()
    if not cart_item:
        raise NotFoundException(f"Cart item not found: {cart_item_id}")
    await db.delete(cart_item)
    await db.commit()


@router.delete("", status_code=204)
async def clear_cart(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Clear the entire cart for the current user."""
    result = await db.execute(
        select(CartItem).where(CartItem.user_id == user_id)
    )
    for ci in result.scalars().all():
        await db.delete(ci)
    await db.commit()


@router.put("", response_model=CartResponse)
async def replace_cart(
    request: BulkReplaceCartRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Atomic cart replacement. Replaces server-side cart state with the provided
    item list in a single DB transaction. Avoids multi-request latency & partial states.
    """
    result = await db.execute(select(CartItem).where(CartItem.user_id == user_id))
    for ci in result.scalars().all():
        await db.delete(ci)
    await db.flush()

    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    has_college, _, allowed_canteen_ids, _ = await get_user_college_info(db, user)

    canteen_ids = set()
    for item_req in request.items:
        menu_result = await db.execute(select(MenuItem).where(MenuItem.id == item_req.menu_item_id))
        menu_item = menu_result.scalars().first()
        if not menu_item:
            raise NotFoundException(f"Menu item not found: {item_req.menu_item_id}")
        if not menu_item.is_available:
            raise BadRequestException(f"'{menu_item.name}' is currently not available")
        if has_college and (not allowed_canteen_ids or menu_item.canteen_id not in allowed_canteen_ids):
            raise BadRequestException("You can only add items from your college canteens to your cart")
        canteen_ids.add(menu_item.canteen_id)
        db.add(CartItem(
            user_id=user_id,
            menu_item_id=item_req.menu_item_id,
            canteen_id=menu_item.canteen_id,
            quantity=item_req.quantity
        ))

    real_canteen_ids = {cid for cid in canteen_ids if cid is not None}
    if len(real_canteen_ids) > 1:
        raise BadRequestException("Cart can contain items from only one canteen at a time")

    await db.commit()
    return await get_cart(db=db, user_id=user_id)


@router.post("/validate", response_model=CartValidateResponse)
async def validate_cart(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Pre-checkout validation. Checks each cart item for:
    - Availability (item might have been turned off)
    Returns a list of issues and the current total.
    """
    result = await db.execute(
        select(CartItem).where(CartItem.user_id == user_id)
    )
    cart_items = result.scalars().all()

    issues = []
    current_total = Decimal("0.00")

    for ci in cart_items:
        item = ci.menu_item
        if not item.is_available:
            issues.append(CartValidateIssue(
                menu_item_id=item.id,
                item_name=item.name,
                issue="UNAVAILABLE"
            ))
        else:
            current_total += Decimal(str(item.price)) * ci.quantity

    return CartValidateResponse(
        is_valid=len(issues) == 0,
        issues=issues,
        current_total=current_total
    )


@router.post("/calculate-bill", response_model=BillResponse)
async def calculate_bill(
    payload: CalculateBillRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Dynamic Checkout Billing & Tax Breakdown API.
    Calculates subtotal, discounts, packaging fees, GST, and returns dynamic breakdown.
    """
    subtotal = Decimal("0.00")
    item_discount_total = Decimal("0.00")
    bill_items: list[BillItemDetail] = []

    for ci in payload.items:
        menu_result = await db.execute(
            select(MenuItem).where(MenuItem.id == ci.menu_item_id)
        )
        menu_item = menu_result.scalars().first()
        if not menu_item:
            raise NotFoundException(f"Menu item not found: {ci.menu_item_id}")

        orig_price = Decimal(str(menu_item.original_price if menu_item.original_price is not None else menu_item.price))
        selling_price = Decimal(str(menu_item.price))
        unit_discount = max(Decimal("0.00"), orig_price - selling_price)
        line_discount = unit_discount * ci.quantity
        line_total = selling_price * ci.quantity

        subtotal += line_total
        item_discount_total += line_discount

        bill_items.append(BillItemDetail(
            menu_item_id=menu_item.id,
            item_name=menu_item.name,
            quantity=ci.quantity,
            original_price=orig_price,
            discount_amount=line_discount,
            final_price=selling_price,
            line_total=line_total,
            prep_time_minutes=menu_item.preparation_time_minutes or 10,
        ))

    # Coupon discount calculation
    coupon_discount = Decimal("0.00")
    applied_coupon_code = None
    if payload.coupon_code:
        code_clean = payload.coupon_code.strip().upper()
        coupon_res = await db.execute(
            select(Coupon).where(Coupon.code == code_clean, Coupon.active == True)
        )
        coupon = coupon_res.scalars().first()
        if coupon:
            if coupon.min_order_amount is None or subtotal >= Decimal(str(coupon.min_order_amount)):
                if coupon.discount_type == "PERCENT":
                    coupon_discount = (subtotal * Decimal(str(coupon.value))) / Decimal("100.00")
                else:
                    coupon_discount = min(Decimal(str(coupon.value)), subtotal)
                if coupon.max_discount_amount is not None:
                    coupon_discount = min(coupon_discount, Decimal(str(coupon.max_discount_amount)))
                coupon_discount = round(coupon_discount, 2)
                applied_coupon_code = code_clean

    # Dynamic fees & taxes
    packaging_fee = Decimal("3.00") if subtotal > 0 else Decimal("0.00")
    gst_fee = round(subtotal * Decimal("0.05"), 2) if subtotal > 0 else Decimal("0.00")
    platform_fee = Decimal("0.00")

    grand_total = max(Decimal("0.00"), subtotal - coupon_discount + packaging_fee + gst_fee + platform_fee)
    total_discount = item_discount_total + coupon_discount

    breakdown = [
        BreakdownItem(
            title="Subtotal",
            amount=subtotal,
            is_discount=False,
            is_highlighted=False,
        )
    ]

    if item_discount_total > 0:
        breakdown.append(BreakdownItem(
            title="Item Discount",
            amount=item_discount_total,
            is_discount=True,
            is_highlighted=True,
        ))

    if coupon_discount > 0 and applied_coupon_code:
        breakdown.append(BreakdownItem(
            title=f"Coupon ({applied_coupon_code})",
            amount=coupon_discount,
            is_discount=True,
            is_highlighted=True,
        ))

    if packaging_fee > 0:
        breakdown.append(BreakdownItem(
            title="Packaging Fee",
            amount=packaging_fee,
            is_discount=False,
            is_highlighted=False,
        ))

    if gst_fee > 0:
        breakdown.append(BreakdownItem(
            title="GST (5%)",
            amount=gst_fee,
            is_discount=False,
            is_highlighted=False,
        ))

    breakdown.append(BreakdownItem(
        title="Platform Fee",
        amount=platform_fee,
        is_discount=False,
        is_highlighted=False,
    ))

    return BillResponse(
        subtotal=subtotal,
        grand_total=grand_total,
        total_discount=total_discount,
        items=bill_items,
        breakdown=breakdown,
    )
