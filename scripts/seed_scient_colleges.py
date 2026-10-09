import asyncio
import os
import sys

# Ensure project root is in Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.database import AsyncSessionLocal, engine
from app.models import College, Canteen, college_canteens, VendorAccount, Category, MenuItem
from app.security import hash_password

COLLEGES = [
    {
        "name": "Scient Institute of Technology",
        "canteens": ["Main Canteen", "Demo Canteen"],
    }
]

VENDORS = [
    {
        "email": "scient.vendor@onfood.com",
        "name": "Scient Main Canteen Vendor",
        "canteen_name": "Main Canteen",
        "raw_password": "Scient@2026",
    },
    {
        "email": "scient_main@onfood.local",
        "name": "Scient Main Canteen Vendor",
        "canteen_name": "Main Canteen",
        "raw_password": "vendor_password",
    },
    {
        "email": "demo.vendor@onfood.com",
        "name": "Demo Canteen Vendor",
        "canteen_name": "Demo Canteen",
        "raw_password": "Demo@2026",
    },
    {
        "email": "demo_canteen@onfood.local",
        "name": "Demo Canteen Vendor",
        "canteen_name": "Demo Canteen",
        "raw_password": "vendor_password",
    }
]

MENU_ITEMS = {
    "Main Canteen": [
        {"name": "Chicken Biryani", "price": "160", "original_price": "190", "discount_percent": "15.79", "category": "Biryani", "image_url": "/images/chicken-biryani.png", "prep": 15, "stock": 50, "special": True},
        {"name": "Veg Dum Biryani", "price": "120", "category": "Biryani", "image_url": "/images/Veg%20Dum%20Biryani.png", "prep": 12, "stock": 40},
        {"name": "Masala Dosa", "price": "60", "category": "South Indian", "image_url": "/images/masala-dosa.png", "prep": 8, "stock": 50},
        {"name": "Tea", "price": "15", "category": "Beverages", "image_url": "/images/tea.png", "prep": 2, "stock": 100},
        {"name": "Samosa", "price": "20", "category": "Snacks", "image_url": "/images/Samosa.png", "prep": 3, "stock": 60},
    ],
    "Demo Canteen": [
        {"name": "Veg Fried Rice", "price": "90", "category": "Chinese", "image_url": "/images/veg-fried-rice.png", "prep": 10, "stock": 30},
        {"name": "Paneer Butter Masala", "price": "160", "category": "Curries", "image_url": "/images/paneer-butter-masala.png", "prep": 15, "stock": 25},
        {"name": "Butter Naan", "price": "40", "category": "Breads", "image_url": "/images/butter-naan.png", "prep": 5, "stock": 50},
        {"name": "Cold Coffee", "price": "50", "category": "Beverages", "image_url": "/images/coffee.png", "prep": 4, "stock": 30},
    ],
}

async def seed_scient_data():
    async with AsyncSessionLocal() as db:
        print("🌱 Seeding Scient Institute of Technology & Demo Canteens...")

        # 1. Colleges
        colleges_map = {}
        for col in COLLEGES:
            res = await db.execute(select(College).where(College.name == col["name"]))
            college_obj = res.scalars().first()
            if not college_obj:
                college_obj = College(name=col["name"])
                db.add(college_obj)
                await db.flush()
                print(f"  + Created college: {col['name']}")
            else:
                print(f"  * College exists: {col['name']}")
            colleges_map[col["name"]] = college_obj

        # 2. Canteens
        all_canteen_names = {"Main Canteen", "Demo Canteen"}
        canteens_map = {}
        for cname in all_canteen_names:
            res = await db.execute(select(Canteen).where(Canteen.name == cname))
            canteen_obj = res.scalars().first()
            if not canteen_obj:
                canteen_obj = Canteen(name=cname)
                db.add(canteen_obj)
                await db.flush()
                print(f"  + Created canteen: {cname}")
            else:
                print(f"  * Canteen exists: {cname}")
            canteens_map[cname] = canteen_obj

        # 3. College <-> Canteens mapping
        for col in COLLEGES:
            college_id = colleges_map[col["name"]].id
            for cname in col["canteens"]:
                canteen_id = canteens_map[cname].id
                await db.execute(
                    pg_insert(college_canteens).values(
                        college_id=college_id,
                        canteen_id=canteen_id,
                    ).on_conflict_do_nothing()
                )
        print("  ✓ Linked colleges and canteens.")

        # 4. Vendors
        for v in VENDORS:
            canteen_id = canteens_map[v["canteen_name"]].id
            res = await db.execute(select(VendorAccount).where(VendorAccount.email == v["email"]))
            v_account = res.scalars().first()
            pwd_hash = hash_password(hashlib.sha256(v["raw_password"].encode()).hexdigest())
            if not v_account:
                v_account = VendorAccount(
                    name=v["name"],
                    email=v["email"],
                    role="admin",
                    canteen_id=canteen_id,
                    hashed_password=pwd_hash,
                    is_active=True,
                )
                db.add(v_account)
                print(f"  + Created vendor account: {v['email']} (Password: {v['raw_password']})")
            else:
                v_account.canteen_id = canteen_id
                v_account.name = v["name"]
                print(f"  * Updated vendor account: {v['email']}")

        # 5. Categories & Menu Items
        cat_res = await db.execute(select(Category))
        categories = {c.name: c for c in cat_res.scalars().all()}

        for cname, items in MENU_ITEMS.items():
            cid = canteens_map[cname].id
            for itm in items:
                cat_obj = categories.get(itm.get("category", "Snacks"))
                cat_id = cat_obj.id if cat_obj else None

                # Check if item already exists for canteen
                m_res = await db.execute(
                    select(MenuItem).where(MenuItem.canteen_id == cid, MenuItem.name == itm["name"])
                )
                m_obj = m_res.scalars().first()
                if not m_obj:
                    m_obj = MenuItem(
                        canteen_id=cid,
                        name=itm["name"],
                        price=itm["price"],
                        original_price=itm.get("original_price"),
                        discount_percent=itm.get("discount_percent"),
                        category_id=cat_id,
                        image_url=itm.get("image_url"),
                        preparation_time_minutes=itm.get("prep", 10),
                        stock=itm.get("stock", 50),
                        special_offer=itm.get("special", False),
                        is_available=True,
                    )
                    db.add(m_obj)
                    print(f"  + Added item '{itm['name']}' to {cname}")

        await db.commit()
        print("✅ Scient Institute of Technology & Canteens successfully seeded!")

if __name__ == "__main__":
    asyncio.run(seed_scient_data())
