from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.config import settings
from app.models import MenuItem, Category, User, Canteen
from app.schemas import (
    CategoryResponse,
    MenuItemResponse,
    MenuPageResponse,
    MenuSyncResponse,
)
from app.cache import get_json, set_json
from app.security import get_current_user_id_optional

router = APIRouter(prefix="/api/menu", tags=["Menu"])


# ─── Helpers ───────────────────────────────────

def _to_menu_response(item: MenuItem) -> MenuItemResponse:
    return MenuItemResponse.model_validate(item)


def _menu_from_json(value: list[dict]) -> list[MenuItemResponse]:
    return [MenuItemResponse.model_validate(item) for item in value]


def _dedupe_menu_items(items: list[MenuItemResponse]) -> list[MenuItemResponse]:
    seen = set()
    deduped = []
    for item in items:
        key = (item.canteen_id, item.name)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


async def _all_cached_menu(db: AsyncSession, canteen_id: Optional[UUID] = None) -> list[MenuItemResponse]:
    cache_key = f"menu:v3:all:{canteen_id or 'all'}"
    cached_items = await get_json(cache_key)
    if cached_items is not None:
        return _dedupe_menu_items(_menu_from_json(cached_items))
    
    stmt = select(MenuItem).join(MenuItem.canteen).where(
        Canteen.is_active == True
    )
    if canteen_id:
        stmt = stmt.where(MenuItem.canteen_id == canteen_id)
    stmt = stmt.order_by(MenuItem.name)
    
    result = await db.execute(stmt)
    items = _dedupe_menu_items([_to_menu_response(i) for i in result.scalars().all()])
    await set_json(cache_key, [item.model_dump(mode="json") for item in items], settings.MENU_CACHE_TTL_SECONDS)
    return items


async def _category_item_counts(db: AsyncSession, canteen_id: Optional[UUID] = None) -> dict:
    stmt = select(MenuItem.category_id, MenuItem.canteen_id, MenuItem.name).join(MenuItem.canteen).where(
        Canteen.is_active == True
    )
    if canteen_id:
        stmt = stmt.where(MenuItem.canteen_id == canteen_id)
    result = await db.execute(stmt.order_by(MenuItem.category_id, MenuItem.canteen_id, MenuItem.name))

    counts: dict = {}
    seen = set()
    for category_id, item_canteen_id, name in result.fetchall():
        key = (item_canteen_id, name)
        if key in seen:
            continue
        seen.add(key)
        counts[category_id] = counts.get(category_id, 0) + 1
    return counts


def _utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _to_utc_naive(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def parse_optional_uuid(val: Optional[str]) -> Optional[UUID]:
    """Parse string to UUID; returns None if string is empty or None."""
    if not val or not val.strip():
        return None
    try:
        return UUID(val.strip())
    except ValueError:
        return None


async def _resolve_canteen_id(
    db: AsyncSession,
    canteen_id_param: Optional[str],
    current_user_id: Optional[str]
) -> Optional[UUID]:
    """
    If canteen_id is explicitly passed in query params, use it.
    Otherwise, if a user token is present, resolve their preferred_canteen_id!
    """
    cid = parse_optional_uuid(canteen_id_param)
    if cid:
        return cid
    if current_user_id:
        user = (await db.execute(select(User).where(User.id == current_user_id))).scalar_one_or_none()
        if user and user.preferred_canteen_id:
            return user.preferred_canteen_id
    return None


# ─── Endpoints ─────────────────────────────────

@router.get("", response_model=List[MenuItemResponse])
async def get_menu(
    canteen_id: Optional[str] = Query(None, alias="canteenId"),
    db: AsyncSession = Depends(get_db),
    current_user_id: Optional[str] = Depends(get_current_user_id_optional)
):
    """All available menu items for the user's canteen (or specified canteenId)."""
    cid = await _resolve_canteen_id(db, canteen_id, current_user_id)
    return await _all_cached_menu(db, cid)


@router.get("/paged", response_model=MenuPageResponse)
async def get_menu_paged(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[str] = Query(None, alias="categoryId"),
    canteen_id: Optional[str] = Query(None, alias="canteenId"),
    db: AsyncSession = Depends(get_db),
    current_user_id: Optional[str] = Depends(get_current_user_id_optional)
):
    """Paged available menu items for fast first paint and infinite scroll."""
    cid = await _resolve_canteen_id(db, canteen_id, current_user_id)
    cat_id = parse_optional_uuid(category_id)
    all_items = await _all_cached_menu(db, cid)
    filtered = [item for item in all_items if not cat_id or item.category_id == cat_id]
    total = len(filtered)
    offset = (page - 1) * limit
    items = filtered[offset:offset + limit]
    return MenuPageResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        has_more=offset + len(items) < total,
    )


@router.get("/sync", response_model=MenuSyncResponse)
async def sync_menu(
    since: Optional[datetime] = Query(None),
    canteen_id: Optional[str] = Query(None, alias="canteenId"),
    db: AsyncSession = Depends(get_db),
    current_user_id: Optional[str] = Depends(get_current_user_id_optional)
):
    """Return menu/category rows changed since the Android app's last sync."""
    cid = await _resolve_canteen_id(db, canteen_id, current_user_id)

    category_query = select(Category)
    item_query = select(MenuItem)
    if cid:
        item_query = item_query.where(MenuItem.canteen_id == cid)
    if since:
        since = _to_utc_naive(since)
        category_query = category_query.where(Category.updated_at > since)
        item_query = item_query.where(MenuItem.updated_at > since)

    category_result = await db.execute(category_query.order_by(Category.display_order))
    item_result = await db.execute(item_query.order_by(MenuItem.name))
    counts = await _category_item_counts(db, cid)

    categories = []
    for cat in category_result.scalars().all():
        response = CategoryResponse.model_validate(cat)
        response.item_count = counts.get(cat.id, 0)
        categories.append(response)

    return MenuSyncResponse(
        categories=categories,
        items=_dedupe_menu_items([_to_menu_response(i) for i in item_result.scalars().all()]),
        server_time=_utc_now_naive(),
    )


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    canteen_id: Optional[str] = Query(None, alias="canteenId"),
    db: AsyncSession = Depends(get_db),
    current_user_id: Optional[str] = Depends(get_current_user_id_optional)
):
    """All active categories with item counts for user's preferred canteen."""
    cid = await _resolve_canteen_id(db, canteen_id, current_user_id)
    cache_key = f"menu:categories:{cid or 'all'}"
    cached_categories = await get_json(cache_key)
    if cached_categories is not None:
        return [CategoryResponse.model_validate(item) for item in cached_categories]
    result = await db.execute(
        select(Category).where(Category.is_active == True).order_by(Category.display_order)
    )
    categories = result.scalars().all()

    counts = await _category_item_counts(db, cid)

    responses = []
    for cat in categories:
        r = CategoryResponse.model_validate(cat)
        r.item_count = counts.get(cat.id, 0)
        responses.append(r)
    await set_json(cache_key, [item.model_dump(mode="json") for item in responses], 300)
    return responses


@router.get("/discounts", response_model=List[MenuItemResponse])
async def get_discount_items(
    canteen_id: Optional[str] = Query(None, alias="canteenId"),
    db: AsyncSession = Depends(get_db),
    current_user_id: Optional[str] = Depends(get_current_user_id_optional)
):
    """Items with active discounts (discount_percent > 0)."""
    cid = await _resolve_canteen_id(db, canteen_id, current_user_id)
    cache_key = f"menu:v3:discounts:{cid or 'all'}"
    cached_items = await get_json(cache_key)
    if cached_items is None:
        items = [item for item in await _all_cached_menu(db, cid) if item.discount_percent and item.discount_percent > 0]
        items.sort(key=lambda item: item.discount_percent, reverse=True)
        cached_items = [item.model_dump(mode="json") for item in items]
        await set_json(cache_key, cached_items, settings.MENU_CACHE_TTL_SECONDS)
    return _menu_from_json(cached_items)


@router.get("/specials", response_model=List[MenuItemResponse])
async def get_special_menu(
    canteen_id: Optional[str] = Query(None, alias="canteenId"),
    db: AsyncSession = Depends(get_db),
    current_user_id: Optional[str] = Depends(get_current_user_id_optional)
):
    """Items flagged as special offer."""
    cid = await _resolve_canteen_id(db, canteen_id, current_user_id)
    cache_key = f"menu:v3:specials:{cid or 'all'}"
    cached_items = await get_json(cache_key)
    if cached_items is None:
        items = [item for item in await _all_cached_menu(db, cid) if item.special_offer]
        cached_items = [item.model_dump(mode="json") for item in items]
        await set_json(cache_key, cached_items, settings.MENU_CACHE_TTL_SECONDS)
    return _menu_from_json(cached_items)


@router.get("/search", response_model=List[MenuItemResponse])
async def search_menu(
    q: str = Query(min_length=1),
    canteen_id: Optional[str] = Query(None, alias="canteenId"),
    db: AsyncSession = Depends(get_db),
    current_user_id: Optional[str] = Depends(get_current_user_id_optional)
):
    """Search menu items by name (case-insensitive)."""
    cid = await _resolve_canteen_id(db, canteen_id, current_user_id)
    query = q.casefold()
    return [item for item in await _all_cached_menu(db, cid) if query in item.name.casefold()]


@router.get("/category/{category_id}", response_model=List[MenuItemResponse])
async def get_items_by_category(
    category_id: str,
    canteen_id: Optional[str] = Query(None, alias="canteenId"),
    db: AsyncSession = Depends(get_db),
    current_user_id: Optional[str] = Depends(get_current_user_id_optional)
):
    """All available items in a specific category."""
    cid = await _resolve_canteen_id(db, canteen_id, current_user_id)
    return [item for item in await _all_cached_menu(db, cid) if str(item.category_id) == category_id]
