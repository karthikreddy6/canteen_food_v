"""
app/services/pickup.py

Generates daily-resetting pickup counter numbers.
Each day starts at #1. Numbers increment per order per day.
"""

import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models import Order


async def get_next_pickup_number(db: AsyncSession) -> tuple[int, datetime.date]:
    """
    Returns (pickup_number, pickup_date).
    Counts today's orders and adds 1.
    """
    today = datetime.date.today()

    result = await db.execute(
        select(func.count(Order.id)).where(Order.pickup_date == today)
    )
    count_today = result.scalar() or 0
    next_number = count_today + 1

    return next_number, today
