import asyncio
import os
import sys

# Ensure project root is in Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.future import select
from sqlalchemy import delete, update
from app.database import AsyncSessionLocal
from app.models import (
    College, Canteen, college_canteens, VendorAccount, User,
    MenuItem, OrderItem, Order, CartItem, Banner, SupportTicket, SupportMessage,
    StaffMember, TimeSlot, CouponUsage, PointsTransaction, UserFcmToken,
    RegistrationOtp, PasswordResetOtp, OrderConfirmationOtp
)

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

        # 0. Check for production Scient Institute of Technology & Main Canteen
        scient_col = (await db.execute(select(College).where(College.name == "Scient Institute of Technology"))).scalars().first()
        main_can = (await db.execute(select(Canteen).where(Canteen.name == "Main Canteen"))).scalars().first()

        target_college_id = scient_col.id if scient_col else None
        target_college_name = scient_col.name if scient_col else None
        target_canteen_id = main_can.id if main_can else None

        # 1. Clean up test users and ALL their related rows (orders, items, tickets, etc.)
        for email in TEST_USER_EMAILS:
            user_res = await db.execute(select(User).where(User.email == email))
            user = user_res.scalars().first()
            if user:
                # Find all order IDs for this user
                order_ids = (await db.execute(select(Order.id).where(Order.user_id == user.id))).scalars().all()
                if order_ids:
                    await db.execute(delete(OrderItem).where(OrderItem.order_id.in_(order_ids)))
                    ticket_ids = (await db.execute(select(SupportTicket.id).where(SupportTicket.order_id.in_(order_ids)))).scalars().all()
                    if ticket_ids:
                        await db.execute(delete(SupportMessage).where(SupportMessage.ticket_id.in_(ticket_ids)))
                        await db.execute(delete(SupportTicket).where(SupportTicket.id.in_(ticket_ids)))
                    await db.execute(delete(Order).where(Order.id.in_(order_ids)))

                # Delete user support tickets & messages
                user_ticket_ids = (await db.execute(select(SupportTicket.id).where(SupportTicket.user_id == user.id))).scalars().all()
                if user_ticket_ids:
                    await db.execute(delete(SupportMessage).where(SupportMessage.ticket_id.in_(user_ticket_ids)))
                    await db.execute(delete(SupportTicket).where(SupportTicket.id.in_(user_ticket_ids)))

                # Delete OTPs, tokens, cart, points, coupon usages
                await db.execute(delete(RegistrationOtp).where(RegistrationOtp.user_id == user.id))
                await db.execute(delete(PasswordResetOtp).where(PasswordResetOtp.user_id == user.id))
                await db.execute(delete(OrderConfirmationOtp).where(OrderConfirmationOtp.user_id == user.id))
                await db.execute(delete(CartItem).where(CartItem.user_id == user.id))
                await db.execute(delete(UserFcmToken).where(UserFcmToken.user_id == user.id))
                await db.execute(delete(CouponUsage).where(CouponUsage.user_id == user.id))
                await db.execute(delete(PointsTransaction).where(PointsTransaction.user_id == user.id))

                # Delete user
                await db.execute(delete(User).where(User.id == user.id))
                print(f"  - Deleted test user & orders: {email}")

        # 2. Delete test vendors
        for email in TEST_VENDOR_EMAILS:
            v_res = await db.execute(select(VendorAccount).where(VendorAccount.email == email))
            v = v_res.scalars().first()
            if v:
                await db.execute(delete(VendorAccount).where(VendorAccount.email == email))
                print(f"  - Deleted test vendor: {email}")

        # 3. Clean up test canteens and all their related rows
        for cname in TEST_CANTEEN_NAMES:
            c_res = await db.execute(select(Canteen).where(Canteen.name == cname))
            c = c_res.scalars().first()
            if c:
                # Re-link any users who selected this test canteen as their preferred canteen
                await db.execute(
                    update(User)
                    .where(User.preferred_canteen_id == c.id)
                    .values(preferred_canteen_id=target_canteen_id)
                )

                # Find all order IDs for this canteen
                c_order_ids = (await db.execute(select(Order.id).where(Order.canteen_id == c.id))).scalars().all()
                if c_order_ids:
                    await db.execute(delete(OrderItem).where(OrderItem.order_id.in_(c_order_ids)))
                    ticket_ids = (await db.execute(select(SupportTicket.id).where(SupportTicket.order_id.in_(c_order_ids)))).scalars().all()
                    if ticket_ids:
                        await db.execute(delete(SupportMessage).where(SupportMessage.ticket_id.in_(ticket_ids)))
                        await db.execute(delete(SupportTicket).where(SupportTicket.id.in_(ticket_ids)))
                    await db.execute(delete(Order).where(Order.id.in_(c_order_ids)))

                await db.execute(delete(CartItem).where(CartItem.canteen_id == c.id))
                await db.execute(delete(MenuItem).where(MenuItem.canteen_id == c.id))
                await db.execute(delete(college_canteens).where(college_canteens.c.canteen_id == c.id))
                await db.execute(delete(VendorAccount).where(VendorAccount.canteen_id == c.id))
                await db.execute(delete(StaffMember).where(StaffMember.canteen_id == c.id))
                await db.execute(delete(TimeSlot).where(TimeSlot.canteen_id == c.id))
                await db.execute(delete(Banner).where(Banner.canteen_id == c.id))
                await db.execute(delete(Canteen).where(Canteen.id == c.id))
                print(f"  - Deleted test canteen: {cname}")

        # 4. Clean up test colleges
        for col_name in TEST_COLLEGE_NAMES:
            col_res = await db.execute(select(College).where(College.name == col_name))
            col = col_res.scalars().first()
            if col:
                # Re-link any users who selected this test college
                await db.execute(
                    update(User)
                    .where(User.college_id == col.id)
                    .values(
                        college_id=target_college_id,
                        college=target_college_name
                    )
                )

                await db.execute(delete(college_canteens).where(college_canteens.c.college_id == col.id))
                await db.execute(delete(Banner).where(Banner.college_id == col.id))
                await db.execute(delete(College).where(College.id == col.id))
                print(f"  - Deleted test college: {col_name}")

        await db.commit()
        print("✨ Database cleanup complete! Only production colleges, canteens, and real data remain.")

if __name__ == "__main__":
    asyncio.run(cleanup_test_data())
