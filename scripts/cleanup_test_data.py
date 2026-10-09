import asyncio
import os
import sys
import hashlib

# Ensure project root is in Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.future import select
from sqlalchemy import delete, update, not_
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.database import AsyncSessionLocal
from app.models import (
    College, Canteen, college_canteens, VendorAccount, User,
    MenuItem, OrderItem, Order, CartItem, Banner, SupportTicket, SupportMessage,
    StaffMember, TimeSlot, CouponUsage, PointsTransaction, UserFcmToken,
    RegistrationOtp, PasswordResetOtp, OrderConfirmationOtp
)
from app.security import hash_password

KEEP_COLLEGE_NAMES = [
    "Scient Institute of Technology",
]

KEEP_CANTEEN_NAMES = [
    "Main Canteen",
    "Demo Canteen",
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

SCIENT_VENDORS = [
    {
        "name": "Scient Main Canteen Vendor",
        "email": "scient.vendor@onfood.com",
        "password": "Scient@2026",
        "role": "admin",
        "canteen_name": "Main Canteen",
    },
    {
        "name": "Scient Main Canteen Vendor (Local)",
        "email": "scient_main@onfood.local",
        "password": "vendor_password",
        "role": "admin",
        "canteen_name": "Main Canteen",
    },
    {
        "name": "Demo Canteen Vendor",
        "email": "demo.vendor@onfood.com",
        "password": "Demo@2026",
        "role": "admin",
        "canteen_name": "Demo Canteen",
    },
    {
        "name": "Demo Canteen Vendor (Local)",
        "email": "demo_canteen@onfood.local",
        "password": "vendor_password",
        "role": "admin",
        "canteen_name": "Demo Canteen",
    },
]

async def cleanup_test_data():
    async with AsyncSessionLocal() as db:
        print("🧹 Cleaning up test accounts, colleges, canteens, and vendors...\n")

        # ── Step 0: Ensure Scient Institute of Technology & Canteens exist ──
        col_res = await db.execute(select(College).where(College.name == KEEP_COLLEGE_NAMES[0]))
        scient_col = col_res.scalars().first()
        if not scient_col:
            scient_col = College(name=KEEP_COLLEGE_NAMES[0], is_active=True)
            db.add(scient_col)
            await db.flush()
            print(f"  ✓ Ensured College: {scient_col.name} (ID: {scient_col.id})")
        else:
            print(f"  ✓ Found College: {scient_col.name} (ID: {scient_col.id})")

        canteen_objs = {}
        for cname in KEEP_CANTEEN_NAMES:
            c_res = await db.execute(select(Canteen).where(Canteen.name == cname))
            c_obj = c_res.scalars().first()
            if not c_obj:
                c_obj = Canteen(name=cname, is_active=True, auto_accept_orders=True)
                db.add(c_obj)
                await db.flush()
                print(f"  ✓ Ensured Canteen: {cname} (ID: {c_obj.id})")
            else:
                print(f"  ✓ Found Canteen: {cname} (ID: {c_obj.id})")
            canteen_objs[cname] = c_obj

            # Link with college
            await db.execute(
                pg_insert(college_canteens).values(
                    college_id=scient_col.id,
                    canteen_id=c_obj.id,
                ).on_conflict_do_nothing()
            )

        main_can = canteen_objs["Main Canteen"]

        # Ensure Scient vendors exist
        for v in SCIENT_VENDORS:
            c_target = canteen_objs[v["canteen_name"]]
            v_acc = (await db.execute(select(VendorAccount).where(VendorAccount.email == v["email"]))).scalars().first()
            pwd_hash = hash_password(hashlib.sha256(v["password"].encode()).hexdigest())
            if not v_acc:
                v_acc = VendorAccount(
                    name=v["name"],
                    email=v["email"],
                    role=v["role"],
                    canteen_id=c_target.id,
                    hashed_password=pwd_hash,
                    is_active=True,
                )
                db.add(v_acc)
            else:
                v_acc.name = v["name"]
                v_acc.canteen_id = c_target.id
                v_acc.hashed_password = pwd_hash

            # Ensure matching User record exists
            u_rec = (await db.execute(select(User).where(User.email == v["email"]))).scalars().first()
            if not u_rec:
                u_rec = User(
                    name=v["name"],
                    email=v["email"],
                    phone="9999999999",
                    phone_verified=True,
                    college=scient_col.name,
                    college_id=scient_col.id,
                    preferred_canteen_id=c_target.id,
                    hashed_password=pwd_hash,
                    status="active",
                )
                db.add(u_rec)
            else:
                u_rec.name = v["name"]
                u_rec.college = scient_col.name
                u_rec.college_id = scient_col.id
                u_rec.preferred_canteen_id = c_target.id
                u_rec.phone_verified = True
                u_rec.hashed_password = pwd_hash

        await db.flush()

        # ── Step 1: Re-link any users pointing to old/test canteens or colleges ──
        keep_canteen_ids = [c.id for c in canteen_objs.values()]
        
        # Point any non-Scient canteen reference to Main Canteen
        await db.execute(
            update(User)
            .where(
                User.preferred_canteen_id.isnot(None),
                not_(User.preferred_canteen_id.in_(keep_canteen_ids))
            )
            .values(preferred_canteen_id=main_can.id)
        )
        print("  ✓ Re-linked all existing users' preferred canteen to Main Canteen.")

        # Point any non-Scient college reference to Scient Institute of Technology
        await db.execute(
            update(User)
            .where(
                User.college_id.isnot(None),
                User.college_id != scient_col.id
            )
            .values(
                college_id=scient_col.id,
                college=scient_col.name
            )
        )
        print("  ✓ Re-linked all existing users' college to Scient Institute of Technology.")

        # ── Step 2: Delete test users & all cascading rows ──
        for email in TEST_USER_EMAILS:
            user = (await db.execute(select(User).where(User.email == email))).scalars().first()
            if user:
                order_ids = (await db.execute(select(Order.id).where(Order.user_id == user.id))).scalars().all()
                if order_ids:
                    # Clear points transactions referencing these orders
                    await db.execute(update(PointsTransaction).where(PointsTransaction.order_id.in_(order_ids)).values(order_id=None))
                    # Clear order items
                    await db.execute(delete(OrderItem).where(OrderItem.order_id.in_(order_ids)))
                    # Clear support tickets & messages for these orders
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

                await db.execute(delete(User).where(User.id == user.id))
                print(f"  - Deleted test user: {email}")

        # ── Step 3: Delete non-production / test canteens ──
        test_canteens = (await db.execute(
            select(Canteen).where(not_(Canteen.id.in_(keep_canteen_ids)))
        )).scalars().all()

        for c in test_canteens:
            cname = c.name
            # Ensure users are unlinked from this canteen
            await db.execute(
                update(User)
                .where(User.preferred_canteen_id == c.id)
                .values(preferred_canteen_id=main_can.id)
            )

            # 3a. TimeSlots & Orders referencing them
            slot_ids = (await db.execute(select(TimeSlot.id).where(TimeSlot.canteen_id == c.id))).scalars().all()
            if slot_ids:
                await db.execute(update(Order).where(Order.scheduled_slot_id.in_(slot_ids)).values(scheduled_slot_id=None))
                await db.execute(delete(TimeSlot).where(TimeSlot.id.in_(slot_ids)))

            # 3b. MenuItems & referencing order items / cart items
            m_ids = (await db.execute(select(MenuItem.id).where(MenuItem.canteen_id == c.id))).scalars().all()
            if m_ids:
                await db.execute(delete(OrderItem).where(OrderItem.menu_item_id.in_(m_ids)))
                await db.execute(delete(CartItem).where(CartItem.menu_item_id.in_(m_ids)))
                await db.execute(delete(MenuItem).where(MenuItem.id.in_(m_ids)))

            # 3c. Orders belonging to this canteen
            c_order_ids = (await db.execute(select(Order.id).where(Order.canteen_id == c.id))).scalars().all()
            if c_order_ids:
                await db.execute(update(PointsTransaction).where(PointsTransaction.order_id.in_(c_order_ids)).values(order_id=None))
                await db.execute(delete(OrderItem).where(OrderItem.order_id.in_(c_order_ids)))
                ticket_ids = (await db.execute(select(SupportTicket.id).where(SupportTicket.order_id.in_(c_order_ids)))).scalars().all()
                if ticket_ids:
                    await db.execute(delete(SupportMessage).where(SupportMessage.ticket_id.in_(ticket_ids)))
                    await db.execute(delete(SupportTicket).where(SupportTicket.id.in_(ticket_ids)))
                await db.execute(delete(Order).where(Order.id.in_(c_order_ids)))

            # 3d. Canteen relationships
            await db.execute(delete(CartItem).where(CartItem.canteen_id == c.id))
            await db.execute(delete(Banner).where(Banner.canteen_id == c.id))
            await db.execute(delete(StaffMember).where(StaffMember.canteen_id == c.id))
            await db.execute(delete(VendorAccount).where(VendorAccount.canteen_id == c.id))
            await db.execute(delete(college_canteens).where(college_canteens.c.canteen_id == c.id))
            await db.execute(delete(Canteen).where(Canteen.id == c.id))
            print(f"  - Deleted test canteen: {cname}")

        # ── Step 4: Delete non-production / test colleges ──
        test_colleges = (await db.execute(
            select(College).where(College.id != scient_col.id)
        )).scalars().all()

        for col in test_colleges:
            col_name = col.name
            await db.execute(
                update(User)
                .where(User.college_id == col.id)
                .values(
                    college_id=scient_col.id,
                    college=scient_col.name
                )
            )
            await db.execute(delete(college_canteens).where(college_canteens.c.college_id == col.id))
            await db.execute(delete(Banner).where(Banner.college_id == col.id))
            await db.execute(delete(College).where(College.id == col.id))
            print(f"  - Deleted test college: {col_name}")

        # ── Step 5: Clean up any obsolete vendor accounts ──
        scient_vendor_emails = [v["email"] for v in SCIENT_VENDORS]
        obsolete_vendors = (await db.execute(
            select(VendorAccount).where(not_(VendorAccount.email.in_(scient_vendor_emails)))
        )).scalars().all()
        for v in obsolete_vendors:
            await db.execute(delete(VendorAccount).where(VendorAccount.id == v.id))
            print(f"  - Deleted obsolete vendor: {v.email}")

        await db.commit()
        print("\n✨ Database cleanup complete! Only Scient Institute of Technology & valid canteens remain.")

if __name__ == "__main__":
    asyncio.run(cleanup_test_data())
