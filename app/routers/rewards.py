from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import BadRequestException, NotFoundException
from app.models import (
    User, BrandCoupon, PointsTransaction, PointsTransactionType,
)
from app.schemas import (
    RewardsSummaryResponse, PointsTransactionResponse, PointsHistoryResponse,
    BrandCouponResponse, ClaimedCouponResponse, BrandCouponAdminResponse,
    CreateBrandCouponRequest, BulkCreateBrandCouponRequest, GrantBonusPointsRequest,
)
from app.security import get_current_user_id_verified, get_current_vendor

router = APIRouter(tags=["Rewards"])


# ─── Helpers ────────────────────────────────────────────────


def _require_premium(user: User) -> None:
    """Raise if user is not a Premium member."""
    if not user.is_premium:
        raise BadRequestException("Premium membership is required to access rewards.")


# ─── Student Endpoints ──────────────────────────────────────


@router.get("/api/rewards/summary", response_model=RewardsSummaryResponse)
async def get_rewards_summary(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id_verified),
):
    """Get reward points balance and premium status."""
    user = (await db.execute(select(User).where(User.id == current_user_id))).scalars().first()
    if not user:
        raise NotFoundException("User not found")
    return RewardsSummaryResponse(
        reward_points_balance=user.reward_points_balance,
        lifetime_points_earned=user.lifetime_points_earned,
        is_premium=user.is_premium,
        premium_expires_at=user.premium_expires_at,
    )


@router.post("/api/rewards/subscribe", response_model=RewardsSummaryResponse)
@router.post("/api/rewards/activate", response_model=RewardsSummaryResponse)
async def activate_premium_membership(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id_verified),
):
    """Activate or subscribe to Premium membership for the logged-in user."""
    user = (await db.execute(select(User).where(User.id == current_user_id))).scalars().first()
    if not user:
        raise NotFoundException("User not found")
    user.is_premium = True
    await db.commit()
    await db.refresh(user)
    return RewardsSummaryResponse(
        reward_points_balance=user.reward_points_balance,
        lifetime_points_earned=user.lifetime_points_earned,
        is_premium=user.is_premium,
        premium_expires_at=user.premium_expires_at,
    )


@router.get("/api/rewards/history", response_model=PointsHistoryResponse)
async def get_points_history(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id_verified),
):
    """Paginated points transaction log. Requires Premium."""
    user = (await db.execute(select(User).where(User.id == current_user_id))).scalars().first()
    if not user:
        raise NotFoundException("User not found")
    _require_premium(user)

    count_result = await db.execute(
        select(func.count(PointsTransaction.id)).where(
            PointsTransaction.user_id == current_user_id
        )
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(PointsTransaction)
        .where(PointsTransaction.user_id == current_user_id)
        .order_by(PointsTransaction.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    transactions = result.scalars().all()

    return PointsHistoryResponse(
        transactions=[
            PointsTransactionResponse(
                id=t.id,
                order_id=t.order_id,
                type=t.type,
                points=t.points,
                balance_after=t.balance_after,
                description=t.description,
                created_at=t.created_at,
            )
            for t in transactions
        ],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/api/rewards/catalog", response_model=List[BrandCouponResponse])
async def get_brand_coupon_catalog(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id_verified),
):
    """Browse available brand coupons. Requires Premium. Only shows unclaimed coupons."""
    user = (await db.execute(select(User).where(User.id == current_user_id))).scalars().first()
    if not user:
        raise NotFoundException("User not found")
    _require_premium(user)

    result = await db.execute(
        select(BrandCoupon)
        .where(
            BrandCoupon.is_active == True,
            BrandCoupon.is_claimed == False,
        )
        .order_by(BrandCoupon.points_cost, BrandCoupon.created_at.desc())
    )
    coupons = result.scalars().all()

    # Group by brand+title+points_cost to show unique catalog entries
    # (many identical codes may exist). We return one entry per unique combo.
    seen = {}
    catalog = []
    for c in coupons:
        key = (c.brand_name, c.title, c.points_cost)
        if key not in seen:
            seen[key] = True
            catalog.append(BrandCouponResponse(
                id=c.id,
                brand_name=c.brand_name,
                brand_logo_url=c.brand_logo_url,
                title=c.title,
                description=c.description,
                points_cost=c.points_cost,
            ))

    return catalog


@router.post("/api/rewards/claim/{coupon_id}", response_model=ClaimedCouponResponse)
async def claim_brand_coupon(
    coupon_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id_verified),
):
    """Spend points to claim a brand coupon. The coupon code is revealed on success."""
    user = (await db.execute(
        select(User).where(User.id == current_user_id).with_for_update()
    )).scalars().first()
    if not user:
        raise NotFoundException("User not found")
    _require_premium(user)

    coupon = (await db.execute(
        select(BrandCoupon)
        .where(
            BrandCoupon.id == coupon_id,
            BrandCoupon.is_active == True,
            BrandCoupon.is_claimed == False,
        )
        .with_for_update()
    )).scalars().first()

    if not coupon:
        raise NotFoundException("Coupon not found or already claimed")

    if user.reward_points_balance < coupon.points_cost:
        raise BadRequestException(
            f"Insufficient points. You have {user.reward_points_balance} points "
            f"but this coupon costs {coupon.points_cost} points."
        )

    # Deduct points
    user.reward_points_balance -= coupon.points_cost

    # Mark coupon as claimed
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    coupon.is_claimed = True
    coupon.claimed_by = current_user_id
    coupon.claimed_at = now

    # Record transaction
    db.add(PointsTransaction(
        user_id=current_user_id,
        type=PointsTransactionType.REDEEMED,
        points=-coupon.points_cost,
        balance_after=user.reward_points_balance,
        description=f"Redeemed {coupon.points_cost} points for {coupon.brand_name}: {coupon.title}",
    ))

    await db.commit()

    return ClaimedCouponResponse(
        id=coupon.id,
        brand_name=coupon.brand_name,
        brand_logo_url=coupon.brand_logo_url,
        title=coupon.title,
        description=coupon.description,
        coupon_code=coupon.coupon_code,
        points_cost=coupon.points_cost,
        claimed_at=coupon.claimed_at,
    )


@router.get("/api/rewards/my-coupons", response_model=List[ClaimedCouponResponse])
async def get_my_claimed_coupons(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id_verified),
):
    """Get all brand coupons the user has claimed (with revealed codes)."""
    user = (await db.execute(select(User).where(User.id == current_user_id))).scalars().first()
    if not user:
        raise NotFoundException("User not found")
    _require_premium(user)

    result = await db.execute(
        select(BrandCoupon)
        .where(
            BrandCoupon.claimed_by == current_user_id,
            BrandCoupon.is_claimed == True,
        )
        .order_by(BrandCoupon.claimed_at.desc())
    )
    coupons = result.scalars().all()

    return [
        ClaimedCouponResponse(
            id=c.id,
            brand_name=c.brand_name,
            brand_logo_url=c.brand_logo_url,
            title=c.title,
            description=c.description,
            coupon_code=c.coupon_code,
            points_cost=c.points_cost,
            claimed_at=c.claimed_at,
        )
        for c in coupons
    ]


# ─── Vendor Endpoints ───────────────────────────────────────


@router.get("/api/vendor/rewards/coupons", response_model=List[BrandCouponAdminResponse])
async def list_brand_coupons(
    db: AsyncSession = Depends(get_db),
    vendor=Depends(get_current_vendor),
):
    """List all brand coupons (claimed + unclaimed) for vendor dashboard."""
    result = await db.execute(
        select(BrandCoupon).order_by(BrandCoupon.created_at.desc())
    )
    coupons = result.scalars().all()
    return [
        BrandCouponAdminResponse(
            id=c.id,
            brand_name=c.brand_name,
            brand_logo_url=c.brand_logo_url,
            title=c.title,
            description=c.description,
            coupon_code=c.coupon_code,
            points_cost=c.points_cost,
            is_claimed=c.is_claimed,
            claimed_by=c.claimed_by,
            claimed_at=c.claimed_at,
            is_active=c.is_active,
            created_at=c.created_at,
        )
        for c in coupons
    ]


@router.post("/api/vendor/rewards/coupons", response_model=BrandCouponAdminResponse, status_code=201)
async def create_brand_coupon(
    request: CreateBrandCouponRequest,
    db: AsyncSession = Depends(get_db),
    vendor=Depends(get_current_vendor),
):
    """Add a single brand coupon to the catalog."""
    coupon = BrandCoupon(
        brand_name=request.brand_name,
        brand_logo_url=request.brand_logo_url,
        title=request.title,
        description=request.description,
        coupon_code=request.coupon_code,
        points_cost=request.points_cost,
    )
    db.add(coupon)
    await db.commit()
    await db.refresh(coupon)
    return BrandCouponAdminResponse(
        id=coupon.id,
        brand_name=coupon.brand_name,
        brand_logo_url=coupon.brand_logo_url,
        title=coupon.title,
        description=coupon.description,
        coupon_code=coupon.coupon_code,
        points_cost=coupon.points_cost,
        is_claimed=coupon.is_claimed,
        claimed_by=coupon.claimed_by,
        claimed_at=coupon.claimed_at,
        is_active=coupon.is_active,
        created_at=coupon.created_at,
    )


@router.post("/api/vendor/rewards/coupons/bulk", status_code=201)
async def bulk_create_brand_coupons(
    request: BulkCreateBrandCouponRequest,
    db: AsyncSession = Depends(get_db),
    vendor=Depends(get_current_vendor),
):
    """Upload a batch of coupon codes for a brand in one call."""
    coupons = []
    for code in request.coupon_codes:
        coupon = BrandCoupon(
            brand_name=request.brand_name,
            brand_logo_url=request.brand_logo_url,
            title=request.title,
            description=request.description,
            coupon_code=code.strip(),
            points_cost=request.points_cost,
        )
        db.add(coupon)
        coupons.append(coupon)
    await db.commit()
    return {"created": len(coupons), "message": f"Added {len(coupons)} {request.brand_name} coupons"}


@router.patch("/api/vendor/rewards/coupons/{coupon_id}", response_model=BrandCouponAdminResponse)
async def update_brand_coupon(
    coupon_id: UUID,
    request: CreateBrandCouponRequest,
    db: AsyncSession = Depends(get_db),
    vendor=Depends(get_current_vendor),
):
    """Update a brand coupon (only if not yet claimed)."""
    coupon = (await db.execute(
        select(BrandCoupon).where(BrandCoupon.id == coupon_id)
    )).scalars().first()
    if not coupon:
        raise NotFoundException("Brand coupon not found")
    if coupon.is_claimed:
        raise BadRequestException("Cannot edit a coupon that has already been claimed")

    coupon.brand_name = request.brand_name
    coupon.brand_logo_url = request.brand_logo_url
    coupon.title = request.title
    coupon.description = request.description
    coupon.coupon_code = request.coupon_code
    coupon.points_cost = request.points_cost
    await db.commit()
    await db.refresh(coupon)
    return BrandCouponAdminResponse(
        id=coupon.id,
        brand_name=coupon.brand_name,
        brand_logo_url=coupon.brand_logo_url,
        title=coupon.title,
        description=coupon.description,
        coupon_code=coupon.coupon_code,
        points_cost=coupon.points_cost,
        is_claimed=coupon.is_claimed,
        claimed_by=coupon.claimed_by,
        claimed_at=coupon.claimed_at,
        is_active=coupon.is_active,
        created_at=coupon.created_at,
    )


@router.delete("/api/vendor/rewards/coupons/{coupon_id}", status_code=204)
async def delete_brand_coupon(
    coupon_id: UUID,
    db: AsyncSession = Depends(get_db),
    vendor=Depends(get_current_vendor),
):
    """Deactivate a brand coupon."""
    coupon = (await db.execute(
        select(BrandCoupon).where(BrandCoupon.id == coupon_id)
    )).scalars().first()
    if not coupon:
        raise NotFoundException("Brand coupon not found")
    coupon.is_active = False
    await db.commit()


@router.post("/api/vendor/rewards/bonus", status_code=201)
async def grant_bonus_points(
    request: GrantBonusPointsRequest,
    db: AsyncSession = Depends(get_db),
    vendor=Depends(get_current_vendor),
):
    """Grant bonus points to a specific user."""
    user = (await db.execute(
        select(User).where(User.id == request.user_id).with_for_update()
    )).scalars().first()
    if not user:
        raise NotFoundException("User not found")
    if not user.is_premium:
        raise BadRequestException("User must be a Premium member to receive bonus points")

    user.reward_points_balance += request.points
    user.lifetime_points_earned += request.points
    db.add(PointsTransaction(
        user_id=request.user_id,
        type=PointsTransactionType.BONUS,
        points=request.points,
        balance_after=user.reward_points_balance,
        description=request.description or f"Bonus: {request.points} points",
    ))
    await db.commit()
    return {
        "userId": user.id,
        "pointsGranted": request.points,
        "newBalance": user.reward_points_balance,
    }


@router.patch("/api/vendor/users/{user_id}/premium")
async def toggle_premium(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    vendor=Depends(get_current_vendor),
):
    """Toggle a user's Premium membership on/off."""
    user = (await db.execute(
        select(User).where(User.id == user_id)
    )).scalars().first()
    if not user:
        raise NotFoundException("User not found")

    user.is_premium = not user.is_premium
    if not user.is_premium:
        user.premium_expires_at = None
    await db.commit()
    return {
        "userId": user.id,
        "isPremium": user.is_premium,
        "message": f"Premium {'activated' if user.is_premium else 'deactivated'} for {user.name}",
    }
