import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import BrandCoupon

brand_coupons = [
    {
        "brand_name": "District",
        "brand_logo_url": "https://play-lh.googleusercontent.com/t0LH2EDF97k1-d2i8kSh_vUlZlnntAGWRYIX8BVSRSAyMGUlNAraa-q4kez1YMKQmGc_9BeEFGmD3wTud5NDOg",
        "title": "₹1000 off on shopping",
        "description": "Get ₹1000 off on shopping orders on District",
        "points_cost": 1000,
        "codes": [
            "DISTRICT1000",
            "DISTRICT1000-01",
            "DISTRICT1000-02",
            "DISTRICT1000-03",
            "DISTRICT1000-04",
            "DISTRICT1000-05",
        ],
    },
    {
        "brand_name": "Swiggy",
        "brand_logo_url": "https://upload.wikimedia.org/wikipedia/en/thumb/1/12/Swiggy_logo.svg/512px-Swiggy_logo.svg.png",
        "title": "₹50 off on Swiggy",
        "description": "Valid on orders above ₹199",
        "points_cost": 500,
        "codes": [
            "SWIGGY50OFF",
            "SWIGGY50-01",
            "SWIGGY50-02",
        ],
    },
    {
        "brand_name": "Zomato",
        "brand_logo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Zomato_logo.png/512px-Zomato_logo.png",
        "title": "₹50 off on Zomato",
        "description": "Valid on orders above ₹199",
        "points_cost": 500,
        "codes": [
            "ZOMATO50OFF",
            "ZOMATO50-01",
            "ZOMATO50-02",
        ],
    },
]

async def seed_brand_coupons():
    async with AsyncSessionLocal() as db:
        for bc in brand_coupons:
            for code in bc["codes"]:
                existing = (
                    await db.execute(
                        select(BrandCoupon).where(
                            BrandCoupon.coupon_code == code,
                            BrandCoupon.brand_name == bc["brand_name"],
                        )
                    )
                ).scalar_one_or_none()

                if existing:
                    existing.brand_logo_url = bc["brand_logo_url"]
                    existing.title = bc["title"]
                    existing.description = bc["description"]
                    existing.points_cost = bc["points_cost"]
                    existing.is_active = True
                    print(f"Updated: {bc['brand_name']} - {code}")
                else:
                    db.add(
                        BrandCoupon(
                            brand_name=bc["brand_name"],
                            brand_logo_url=bc["brand_logo_url"],
                            title=bc["title"],
                            description=bc["description"],
                            coupon_code=code,
                            points_cost=bc["points_cost"],
                            is_claimed=False,
                            is_active=True,
                        )
                    )
                    print(f"Created: {bc['brand_name']} - {code}")
        await db.commit()
        print("Brand coupons seeding finished successfully.")

if __name__ == "__main__":
    asyncio.run(seed_brand_coupons())
