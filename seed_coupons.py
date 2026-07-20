import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import Coupon

coupons = [
    dict(
        code="SAVE10",
        discount_type="PERCENT",
        value=10,
        min_order_amount=None,
        max_discount_amount=None,
        active=True,
        max_uses=None,
        per_user_limit=None,      # unlimited use, unlimited users
    ),
    dict(
        code="FLAT25",
        discount_type="FIXED",
        value=25,
        min_order_amount=150,     # only on orders >= Rs 150
        max_discount_amount=25,   # max Rs 25 off
        active=True,
        max_uses=None,
        per_user_limit=1,         # each user can use once only
    ),
    dict(
        code="FLAT50",
        discount_type="FIXED",
        value=50,
        min_order_amount=600,     # only on orders >= Rs 600
        max_discount_amount=50,   # max Rs 50 off
        active=True,
        max_uses=None,
        per_user_limit=1,         # each user can use once only
    ),
]

async def seed():
    async with AsyncSessionLocal() as db:
        for c in coupons:
            existing = (await db.execute(select(Coupon).where(Coupon.code == c["code"]))).scalar_one_or_none()
            if existing:
                for k, v in c.items():
                    setattr(existing, k, v)
                print("Updated:", c["code"])
            else:
                db.add(Coupon(**c))
                print("Created:", c["code"])
        await db.commit()
        print("Done.")

asyncio.run(seed())
