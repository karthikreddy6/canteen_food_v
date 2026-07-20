from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import BadRequestException, NotFoundException
from app.models import Banner, Coupon, CouponUsage, MenuItem, User
from app.security import get_current_vendor, get_current_user_id
from app.schemas import CamelModel

router = APIRouter(tags=["Promotions"])


class CouponRequest(CamelModel):
    code: str
    discount_type: str = "PERCENT"             # "PERCENT" or "FIXED"
    value: Decimal                              # 10 = 10% or ₹10 fixed
    min_order_amount: Optional[Decimal] = None  # Minimum cart total to apply
    max_discount_amount: Optional[Decimal] = None  # Cap (e.g. max ₹25 off)
    active: bool = True
    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = None             # Global usage cap (None = unlimited)
    per_user_limit: Optional[int] = None       # Per-user cap (1 = one-time, None = unlimited)


class CouponApplyItem(CamelModel):
    menu_item_id: UUID
    quantity: int


class CouponApplyRequest(CamelModel):
    coupon_code: str
    items: List[CouponApplyItem]


class BannerRequest(CamelModel):
    title: str
    image_url: str
    link_url: Optional[str] = None
    is_active: bool = True
    display_order: int = 0
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    college_id: Optional[UUID] = None
    canteen_id: Optional[UUID] = None


def coupon_json(coupon: Coupon) -> dict:
    """Public-facing coupon info shown to students — no internal counters."""
    return {
        "code": coupon.code,
        "discountType": coupon.discount_type,
        "value": str(coupon.value),
        "minOrderAmount": str(coupon.min_order_amount) if coupon.min_order_amount is not None else None,
        "maxDiscountAmount": str(coupon.max_discount_amount) if coupon.max_discount_amount is not None else None,
        "expiresAt": coupon.expires_at.isoformat() if coupon.expires_at else None,
        "perUserLimit": coupon.per_user_limit,
    }


def coupon_admin_json(coupon: Coupon) -> dict:
    """Full coupon info for vendor/admin dashboards."""
    return {
        "id": str(coupon.id),
        "code": coupon.code,
        "discountType": coupon.discount_type,
        "value": str(coupon.value),
        "minOrderAmount": str(coupon.min_order_amount) if coupon.min_order_amount is not None else None,
        "maxDiscountAmount": str(coupon.max_discount_amount) if coupon.max_discount_amount is not None else None,
        "active": coupon.active,
        "expiresAt": coupon.expires_at.isoformat() if coupon.expires_at else None,
        "maxUses": coupon.max_uses,
        "usedCount": coupon.used_count,
        "perUserLimit": coupon.per_user_limit,
    }


def banner_json(banner: Banner) -> dict:
    return {
        "id": str(banner.id), "title": banner.title,
        "imageUrl": banner.image_url, "linkUrl": banner.link_url,
        "isActive": banner.is_active, "displayOrder": banner.display_order,
        "startsAt": banner.starts_at, "endsAt": banner.ends_at,
        "collegeId": str(banner.college_id) if banner.college_id else None,
        "canteenId": str(banner.canteen_id) if banner.canteen_id else None,
    }


# ─── Student Endpoints ──────────────────────────────────────

@router.get("/api/banners")
async def get_banners(db: AsyncSession = Depends(get_db), current_user_id: str = Depends(get_current_user_id)):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    user = (await db.execute(select(User).where(User.id == current_user_id))).scalar_one_or_none()
    if not user:
        return []
    result = await db.execute(
        select(Banner)
        .where(Banner.is_active == True)
        .where((Banner.starts_at == None) | (Banner.starts_at <= now))
        .where((Banner.ends_at == None) | (Banner.ends_at > now))
        .where(or_(Banner.college_id == user.college_id, Banner.college_id == None))
        .where(or_(Banner.canteen_id == user.preferred_canteen_id, Banner.canteen_id == None))
        .order_by(Banner.display_order, Banner.created_at.desc())
    )
    return [banner_json(item) for item in result.scalars().all()]


@router.get("/api/coupons/{code}")
async def validate_coupon(code: str, db: AsyncSession = Depends(get_db)):
    """
    Look up a coupon by code. Returns clean public info.
    404 if not found, expired, or inactive.
    """
    result = await db.execute(select(Coupon).where(Coupon.code == code.strip().upper()))
    coupon = result.scalar_one_or_none()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if not coupon or not coupon.active:
        raise NotFoundException("Coupon not found or expired")
    if coupon.expires_at and coupon.expires_at.replace(tzinfo=None) <= now:
        raise NotFoundException("Coupon has expired")
    if coupon.max_uses is not None and coupon.used_count >= coupon.max_uses:
        raise BadRequestException("Coupon usage limit has been reached")
    return coupon_json(coupon)


@router.post("/api/coupons/apply")
async def apply_coupon(
    request: CouponApplyRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Calculate a coupon preview for the supplied item IDs and quantities."""
    code = request.coupon_code.strip().upper()
    if not request.items:
        raise BadRequestException("At least one cart item is required")
    if any(item.quantity < 1 for item in request.items):
        raise BadRequestException("Item quantities must be at least 1")

    coupon_result = await db.execute(select(Coupon).where(Coupon.code == code))
    coupon = coupon_result.scalar_one_or_none()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if not coupon or not coupon.active:
        raise BadRequestException("Coupon is invalid or inactive")
    if coupon.expires_at and coupon.expires_at.replace(tzinfo=None) <= now:
        raise BadRequestException("Coupon has expired")
    if coupon.max_uses is not None and coupon.used_count >= coupon.max_uses:
        raise BadRequestException("Coupon usage limit has been reached")

    usage_count = await db.execute(
        select(CouponUsage).where(
            CouponUsage.coupon_id == coupon.id,
            CouponUsage.user_id == current_user_id,
        )
    )
    if coupon.per_user_limit is not None and len(usage_count.scalars().all()) >= coupon.per_user_limit:
        raise BadRequestException("You have already used this coupon the maximum number of times")

    item_ids = [item.menu_item_id for item in request.items]
    menu_result = await db.execute(select(MenuItem).where(MenuItem.id.in_(item_ids)))
    menu_items = {item.id: item for item in menu_result.scalars().all()}
    subtotal = Decimal("0.00")
    response_items = []
    for cart_item in request.items:
        menu_item = menu_items.get(cart_item.menu_item_id)
        if not menu_item:
            raise NotFoundException(f"Menu item not found: {cart_item.menu_item_id}")
        if not menu_item.is_available:
            raise BadRequestException(f"'{menu_item.name}' is currently not available")
        item_price = Decimal(str(menu_item.price))
        line_total = (item_price * cart_item.quantity).quantize(Decimal("0.01"))
        subtotal += line_total
        response_items.append({
            "menuItemId": str(menu_item.id),
            "quantity": cart_item.quantity,
            "itemPrice": str(item_price),
            "lineTotal": str(line_total),
        })

    if coupon.min_order_amount is not None and subtotal < Decimal(str(coupon.min_order_amount)):
        raise BadRequestException(
            f"This coupon requires a minimum order of ₹{coupon.min_order_amount}."
        )
    if coupon.discount_type.upper() == "PERCENT":
        discount = subtotal * Decimal(str(coupon.value)) / Decimal("100")
    else:
        discount = min(subtotal, Decimal(str(coupon.value)))
    if coupon.max_discount_amount is not None:
        discount = min(discount, Decimal(str(coupon.max_discount_amount)))
    discount = discount.quantize(Decimal("0.01"))

    return {
        "couponCode": code,
        "isValid": True,
        "items": response_items,
        "subtotal": str(subtotal.quantize(Decimal("0.01"))),
        "discountAmount": str(discount),
        "totalAmount": str((subtotal - discount).quantize(Decimal("0.01"))),
        "message": "Coupon applied successfully",
    }


# ─── Vendor Endpoints ───────────────────────────────────────

@router.get("/api/vendor/coupons")
async def list_coupons(db: AsyncSession = Depends(get_db), vendor=Depends(get_current_vendor)):
    result = await db.execute(select(Coupon).order_by(Coupon.created_at.desc()))
    return [coupon_admin_json(item) for item in result.scalars().all()]


@router.post("/api/vendor/coupons", status_code=201)
async def create_coupon(request: CouponRequest, db: AsyncSession = Depends(get_db), vendor=Depends(get_current_vendor)):
    code = request.code.strip().upper()
    if request.discount_type.upper() not in {"PERCENT", "FIXED"}:
        raise BadRequestException("discountType must be PERCENT or FIXED")
    if request.value < 0 or (request.discount_type.upper() == "PERCENT" and request.value > 100):
        raise BadRequestException("Invalid coupon value")
    data = request.model_dump(exclude={"code", "discount_type"})
    coupon = Coupon(code=code, discount_type=request.discount_type.upper(), **data)
    db.add(coupon)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise BadRequestException("Coupon code already exists")
    await db.refresh(coupon)
    return coupon_admin_json(coupon)


@router.patch("/api/vendor/coupons/{coupon_id}")
async def update_coupon(coupon_id: UUID, request: CouponRequest, db: AsyncSession = Depends(get_db), vendor=Depends(get_current_vendor)):
    result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = result.scalar_one_or_none()
    if not coupon:
        raise NotFoundException("Coupon not found")
    for field, value in request.model_dump().items():
        setattr(coupon, field, value.upper() if field in {"code", "discount_type"} else value)
    await db.commit()
    await db.refresh(coupon)
    return coupon_admin_json(coupon)


# ─── Banner Vendor Endpoints ────────────────────────────────

@router.get("/api/vendor/banners")
async def list_banners(db: AsyncSession = Depends(get_db), vendor=Depends(get_current_vendor)):
    result = await db.execute(select(Banner).order_by(Banner.display_order, Banner.created_at.desc()))
    return [banner_json(item) for item in result.scalars().all()]


@router.post("/api/vendor/banners", status_code=201)
async def create_banner(request: BannerRequest, db: AsyncSession = Depends(get_db), vendor=Depends(get_current_vendor)):
    banner = Banner(**request.model_dump())
    db.add(banner)
    await db.commit()
    await db.refresh(banner)
    return banner_json(banner)


@router.patch("/api/vendor/banners/{banner_id}")
async def update_banner(banner_id: UUID, request: BannerRequest, db: AsyncSession = Depends(get_db), vendor=Depends(get_current_vendor)):
    result = await db.execute(select(Banner).where(Banner.id == banner_id))
    banner = result.scalar_one_or_none()
    if not banner:
        raise NotFoundException("Banner not found")
    for field, value in request.model_dump().items():
        setattr(banner, field, value)
    await db.commit()
    await db.refresh(banner)
    return banner_json(banner)
