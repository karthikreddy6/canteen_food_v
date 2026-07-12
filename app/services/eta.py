"""
app/services/eta.py

Intelligent ETA calculation engine for OnFood kitchen.

ETA Formula:
  base_prep = MAX(preparation_time_minutes of all ordered items)
  queue_buffer = (active_orders_count - 1) * base_prep_buffer_minutes
                 (0 if this is the first/only order)
  total_minutes = base_prep + queue_buffer
"""

import datetime
from decimal import Decimal
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models import Order, OrderItem, MenuItem, OrderStatus, KitchenSettings


async def get_kitchen_settings(db: AsyncSession) -> KitchenSettings:
    """Fetch kitchen settings row (always id=1). Auto-creates if missing."""
    result = await db.execute(select(KitchenSettings).where(KitchenSettings.id == 1))
    settings = result.scalars().first()
    if not settings:
        settings = KitchenSettings(
            id=1,
            base_prep_buffer_minutes=3,
            max_concurrent_orders=20,
            is_accepting_orders=True
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


async def count_active_orders(db: AsyncSession) -> int:
    """Count orders currently PENDING or PREPARING."""
    result = await db.execute(
        select(func.count(Order.id)).where(
            Order.status.in_([OrderStatus.PLACED, OrderStatus.PREPARING])
        )
    )
    return result.scalar() or 0


async def calculate_eta(
    db: AsyncSession,
    menu_item_ids: List,
) -> dict:
    """
    Calculate ETA for a set of menu item ids being ordered.
    Returns dict with estimated_minutes, estimated_ready_at,
    base_prep_minutes, queue_buffer_minutes.
    """
    settings = await get_kitchen_settings(db)
    active_count = await count_active_orders(db)

    # Fetch prep times for ordered items
    result = await db.execute(
        select(MenuItem.preparation_time_minutes).where(
            MenuItem.id.in_(menu_item_ids)
        )
    )
    prep_times = [row[0] for row in result.fetchall()]
    base_prep = max(prep_times) if prep_times else 10

    # Queue buffer: each active order (beyond this one) adds buffer
    # active_count is BEFORE this order is inserted
    queue_buffer = max(0, active_count) * settings.base_prep_buffer_minutes

    total_minutes = base_prep + queue_buffer

    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    estimated_ready_at = now + datetime.timedelta(minutes=total_minutes)

    return {
        "estimated_minutes": total_minutes,
        "estimated_ready_at": estimated_ready_at,
        "base_prep_minutes": base_prep,
        "queue_buffer_minutes": queue_buffer,
        "active_orders_count": active_count,
    }
