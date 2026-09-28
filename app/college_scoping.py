from typing import Optional, Set, Tuple
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, College, Canteen, college_canteens
from app.exceptions import BadRequestException


def parse_optional_uuid(val: Optional[str]) -> Optional[UUID]:
    """Parse string to UUID; returns None if string is empty or None."""
    if not val or not val.strip():
        return None
    try:
        return UUID(val.strip())
    except ValueError:
        return None


async def get_user_college_info(
    db: AsyncSession,
    user: Optional[User],
) -> Tuple[bool, Optional[UUID], Set[UUID], Optional[UUID]]:
    """
    Returns (has_college, college_id, allowed_canteen_ids, preferred_canteen_id).
    - has_college: True if the user belongs to a college.
    - college_id: Resolved college UUID if available.
    - allowed_canteen_ids: Set of canteen UUIDs belonging to the user's college.
    - preferred_canteen_id: The user's preferred canteen UUID.
    """
    if not user:
        return (False, None, set(), None)

    college_id = user.college_id
    if not college_id and user.college:
        row = (await db.execute(
            select(College.id).where(func.lower(College.name) == user.college.strip().lower())
        )).scalar_one_or_none()
        if row:
            college_id = row

    if not college_id and user.preferred_canteen_id:
        row = (await db.execute(
            select(college_canteens.c.college_id).where(
                college_canteens.c.canteen_id == user.preferred_canteen_id
            )
        )).scalar_one_or_none()
        if row:
            college_id = row

    has_college = (college_id is not None) or bool(user.college)

    allowed_canteen_ids: Set[UUID] = set()
    if college_id:
        rows = (await db.execute(
            select(college_canteens.c.canteen_id).where(college_canteens.c.college_id == college_id)
        )).scalars().all()
        allowed_canteen_ids = set(rows)

    if user.preferred_canteen_id:
        if not allowed_canteen_ids:
            allowed_canteen_ids.add(user.preferred_canteen_id)

    return (has_college, college_id, allowed_canteen_ids, user.preferred_canteen_id)


class MenuScope:
    def __init__(
        self,
        canteen_id: Optional[UUID] = None,
        canteen_ids: Optional[Set[UUID]] = None,
        college_id: Optional[UUID] = None,
        empty: bool = False,
    ):
        self.canteen_id = canteen_id
        self.canteen_ids = canteen_ids or set()
        self.college_id = college_id
        self.empty = empty


async def resolve_menu_scope(
    db: AsyncSession,
    canteen_id_param: Optional[str],
    college_id_param: Optional[str],
    current_user_id: Optional[str],
) -> MenuScope:
    """
    Resolves the scoping constraint for menu item queries.
    Enforces that an authenticated user can only view their college menu items.
    """
    user: Optional[User] = None
    if current_user_id:
        user = (await db.execute(select(User).where(User.id == current_user_id))).scalar_one_or_none()

    has_college, user_college_id, allowed_canteen_ids, preferred_canteen_id = await get_user_college_info(db, user)

    param_college_id = parse_optional_uuid(college_id_param)
    requested_cid = parse_optional_uuid(canteen_id_param)

    if has_college:
        # College-bound user: MUST only see their college's items
        if param_college_id and user_college_id and param_college_id != user_college_id:
            raise BadRequestException("You can only view menu items from your college")

        if not allowed_canteen_ids:
            # User has a college, but no active canteens in their college -> see nothing
            return MenuScope(empty=True, college_id=user_college_id)

        if requested_cid:
            if requested_cid not in allowed_canteen_ids:
                raise BadRequestException("Selected canteen does not belong to your college")
            return MenuScope(canteen_id=requested_cid, college_id=user_college_id)

        # No specific canteen requested: default to preferred canteen if valid, else all college canteens
        if preferred_canteen_id and preferred_canteen_id in allowed_canteen_ids:
            return MenuScope(canteen_id=preferred_canteen_id, college_id=user_college_id)

        return MenuScope(canteen_ids=allowed_canteen_ids, college_id=user_college_id)

    # Unauthenticated / user without college
    if param_college_id:
        rows = (await db.execute(
            select(college_canteens.c.canteen_id).where(college_canteens.c.college_id == param_college_id)
        )).scalars().all()
        college_cids = set(rows)
        if not college_cids:
            return MenuScope(empty=True, college_id=param_college_id)

        if requested_cid:
            if requested_cid not in college_cids:
                raise BadRequestException("Selected canteen does not belong to the specified college")
            return MenuScope(canteen_id=requested_cid, college_id=param_college_id)

        return MenuScope(canteen_ids=college_cids, college_id=param_college_id)

    if requested_cid:
        return MenuScope(canteen_id=requested_cid)

    return MenuScope()
