from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import CartItem, MenuItem
from app.schemas import (
    CartResponse, CartItemResponse, AddToCartRequest,
    UpdateCartItemRequest, CartValidateResponse, CartValidateIssue
)
from app.security import get_current_user_id
from app.exceptions import NotFoundException, BadRequestException

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
