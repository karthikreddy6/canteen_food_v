from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.models import MenuItem, Category
from app.schemas import MenuItemResponse, CategoryResponse
from app.cache import cached

router = APIRouter(prefix="/api/menu", tags=["Menu"])


# ─── Helpers ───────────────────────────────────

def _to_menu_response(item: MenuItem) -> MenuItemResponse:
    return MenuItemResponse.model_validate(item)


# ─── Endpoints ─────────────────────────────────

@router.get("", response_model=List[MenuItemResponse])
@cached(ttl=120, key="menuItems")
async def get_menu(db: AsyncSession = Depends(get_db)):
    """All available menu items (cached 2 min)."""
    result = await db.execute(
        select(MenuItem).where(MenuItem.is_available == True).order_by(MenuItem.name)
    )
    return [_to_menu_response(i) for i in result.scalars().all()]


@router.get("/categories", response_model=List[CategoryResponse])
@cached(ttl=300, key="menuCategories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """All active categories with item counts."""
    result = await db.execute(
        select(Category).where(Category.is_active == True).order_by(Category.display_order)
    )
    categories = result.scalars().all()

    # Count available items per category
    counts_result = await db.execute(
        select(MenuItem.category_id, func.count(MenuItem.id))
        .where(MenuItem.is_available == True)
        .group_by(MenuItem.category_id)
    )
    counts = {row[0]: row[1] for row in counts_result.fetchall()}

    responses = []
    for cat in categories:
        r = CategoryResponse.model_validate(cat)
        r.item_count = counts.get(cat.id, 0)
        responses.append(r)
    return responses


@router.get("/category/{category_id}", response_model=List[MenuItemResponse])
async def get_items_by_category(category_id: str, db: AsyncSession = Depends(get_db)):
    """All available items in a specific category."""
    result = await db.execute(
        select(MenuItem)
        .where(MenuItem.category_id == category_id, MenuItem.is_available == True)
        .order_by(MenuItem.name)
    )
    return [_to_menu_response(i) for i in result.scalars().all()]


@router.get("/discounts", response_model=List[MenuItemResponse])
@cached(ttl=120, key="discountItems")
async def get_discount_items(db: AsyncSession = Depends(get_db)):
    """Items with active discounts (discount_percent > 0)."""
    result = await db.execute(
        select(MenuItem)
        .where(
            MenuItem.is_available == True,
            MenuItem.discount_percent != None,
            MenuItem.discount_percent > 0
        )
        .order_by(MenuItem.discount_percent.desc())
    )
    return [_to_menu_response(i) for i in result.scalars().all()]


@router.get("/specials", response_model=List[MenuItemResponse])
@cached(ttl=120, key="specialMenuItems")
async def get_special_menu(db: AsyncSession = Depends(get_db)):
    """Items flagged as special offer."""
    result = await db.execute(
        select(MenuItem)
        .where(MenuItem.special_offer == True, MenuItem.is_available == True)
    )
    return [_to_menu_response(i) for i in result.scalars().all()]


@router.get("/search", response_model=List[MenuItemResponse])
async def search_menu(q: str = Query(min_length=1), db: AsyncSession = Depends(get_db)):
    """Search menu items by name (case-insensitive)."""
    result = await db.execute(
        select(MenuItem)
        .where(
            MenuItem.is_available == True,
            MenuItem.name.ilike(f"%{q}%")
        )
    )
    return [_to_menu_response(i) for i in result.scalars().all()]
