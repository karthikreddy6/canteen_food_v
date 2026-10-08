import asyncio
import os
import sys

# Ensure project root is in Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.future import select
from sqlalchemy import delete
from app.database import AsyncSessionLocal, engine
from app.models import (
    College, Canteen, college_canteens, VendorAccount, User,
    MenuItem, OrderItem, Order, CartItem, Banner, SupportTicket, StaffMember
)

# Test items to permanently remove
TEST_COLLEGE_NAMES = [
    "Engineering College",
    "Business College",
    "Arts College",
    "Science College",
    "Demo College",
]

TEST_CANTEEN_NAMES = [
    "Central Canteen",
    "Hostel Canteen",
    "MBA Canteen",
    "Food Court Express",
    "Arts Canteen",
    "Science Canteen",
]

TEST_VENDOR_EMAILS = [
    "central@onfood.local",
    "hostel@onfood.local",
    "mba@onfood.local",
    "express@onfood.local",
    "arts@onfood.local",
    "science@onfood.local",
]

TEST_USER_EMAILS = [
    "karthik@example.com",
    "premium@example.com",
    "student@example.com",
    "holdtester@example.com",
    "holdlogin@example.com",
    "holdrefresh@example.com",
    "eng_student@test.com",
    "arts_student@test.com",
]

async def cleanup_test_data():
    async with AsyncSessionLocal() as db:
        print("🧹 Cleaning up test accounts, colleges, canteens, and vendors...")

        # 1. Delete test users
        for email in TEST_USER_EMAILS:
            user_res = await db.execute(select(User).where(User.email == email))
            user = user_res.scalars().first()
            if user:
                # Delete user cart, orders, etc.
                await db.execute(delete(CartItem).where(CartItem.user_id == user.id))
                await db.execute(delete(User).where(User.id == user.id))
                print(f"  - Deleted test user: {email}")

        # 2. Delete test vendors
        for email in TEST_VENDOR_EMAILS:
            v_res = await db.execute(select(VendorAccount).where(VendorAccount.email == email))
            v = v_res.scalars().first()
            if v:
                await db.execute(delete(VendorAccount).where(VendorAccount.email == email))
                print(f"  - Deleted test vendor: {email}")

        # 3. Find test canteens and clean their related data
        for cname in TEST_CANTEEN_NAMES:
            c_res = await db.execute(select(Canteen).where(Canteen.name == cname))
            c = c_res.scalars().first()
            if c:
                # Delete menu items for this canteen
                await db.execute(delete(CartItem).where(CartItem.canteen_id == c.id))
                await db.execute(delete(MenuItem).where(MenuItem.canteen_id == c.id))
                await db.execute(delete(college_canteens).where(college_canteens.c.canteen_id == c.id))
                await db.execute(delete(VendorAccount).where(VendorAccount.canteen_id == c.id))
                await db.execute(delete(StaffMember).where(StaffMember.canteen_id == c.id))
                await db.execute(delete(Canteen).where(Canteen.id == c.id))
                print(f"  - Deleted test canteen: {cname}")

        # 4. Find test colleges and clean their related data
        for col_name in TEST_COLLEGE_NAMES:
            col_res = await db.execute(select(College).where(College.name == col_name))
            col = col_res.scalars().first()
            if col:
                await db.execute(delete(college_canteens).where(college_canteens.c.college_id == col.id))
                await db.execute(delete(Banner).where(Banner.college_id == col.id))
                await db.execute(delete(College).where(College.id == col.id))
                print(f"  - Deleted test college: {col_name}")

        await db.commit()
        print("✨ Database cleanup complete! Only production colleges and canteens remain.")

if __name__ == "__main__":
    asyncio.run(cleanup_test_data())
