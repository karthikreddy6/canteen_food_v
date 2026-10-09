import asyncio
import os
import sys
import hashlib

# Ensure project root is in Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.database import AsyncSessionLocal
from app.models import College, Canteen, college_canteens, VendorAccount, User
from app.security import hash_password

COLLEGE_NAME = "Scient Institute of Technology"

CANTEENS = [
    {"name": "Main Canteen", "auto_accept": True},
    {"name": "Demo Canteen", "auto_accept": True},
]

VENDORS = [
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

async def create_scient_vendors():
    async with AsyncSessionLocal() as db:
        print("🏢 Setting up Scient Institute of Technology College, Canteens, and Vendors...\n")

        # 1. Ensure College exists
        col_res = await db.execute(select(College).where(College.name == COLLEGE_NAME))
        college = col_res.scalars().first()
        if not college:
            college = College(name=COLLEGE_NAME, is_active=True)
            db.add(college)
            await db.flush()
            print(f"  ✓ Created College: {COLLEGE_NAME} (ID: {college.id})")
        else:
            print(f"  ✓ Found College: {COLLEGE_NAME} (ID: {college.id})")

        # 2. Ensure Canteens exist
        canteen_map = {}
        for c_data in CANTEENS:
            cname = c_data["name"]
            can_res = await db.execute(select(Canteen).where(Canteen.name == cname))
            canteen = can_res.scalars().first()
            if not canteen:
                canteen = Canteen(name=cname, is_active=True, auto_accept_orders=c_data["auto_accept"])
                db.add(canteen)
                await db.flush()
                print(f"  ✓ Created Canteen: {cname} (ID: {canteen.id})")
            else:
                print(f"  ✓ Found Canteen: {cname} (ID: {canteen.id})")
            canteen_map[cname] = canteen

            # Link College & Canteen
            await db.execute(
                pg_insert(college_canteens).values(
                    college_id=college.id,
                    canteen_id=canteen.id,
                ).on_conflict_do_nothing()
            )
            print(f"  ✓ Linked '{cname}' to '{COLLEGE_NAME}'")

        # 3. Create/Upsert Vendor Accounts
        created_accounts = []
        for v in VENDORS:
            canteen = canteen_map[v["canteen_name"]]
            v_res = await db.execute(select(VendorAccount).where(VendorAccount.email == v["email"]))
            vendor = v_res.scalars().first()
            pwd_hash = hash_password(hashlib.sha256(v["password"].encode()).hexdigest())

            if not vendor:
                vendor = VendorAccount(
                    name=v["name"],
                    email=v["email"],
                    role=v["role"],
                    canteen_id=canteen.id,
                    hashed_password=pwd_hash,
                    is_active=True,
                )
                db.add(vendor)
                print(f"  + Created Vendor Account: {v['email']}")
            else:
                vendor.name = v["name"]
                vendor.canteen_id = canteen.id
                vendor.role = v["role"]
                vendor.hashed_password = pwd_hash
                vendor.is_active = True
                print(f"  * Updated Vendor Account: {v['email']}")

            # Also ensure a corresponding User record exists for app login compatibility
            u_res = await db.execute(select(User).where(User.email == v["email"]))
            user = u_res.scalars().first()
            if not user:
                user = User(
                    name=v["name"],
                    email=v["email"],
                    phone="9999999999",
                    phone_verified=True,
                    college=COLLEGE_NAME,
                    college_id=college.id,
                    preferred_canteen_id=canteen.id,
                    hashed_password=pwd_hash,
                    status="active",
                )
                db.add(user)
                print(f"  + Created matching User record: {v['email']}")
            else:
                user.name = v["name"]
                user.college = COLLEGE_NAME
                user.college_id = college.id
                user.preferred_canteen_id = canteen.id
                user.hashed_password = pwd_hash
                user.phone_verified = True
                print(f"  * Updated matching User record: {v['email']}")

            created_accounts.append({
                "name": v["name"],
                "email": v["email"],
                "password": v["password"],
                "canteen": v["canteen_name"],
                "college": COLLEGE_NAME,
                "role": v["role"],
            })

        await db.commit()
        print("\n" + "=" * 65)
        print("🎉 SCIENT INSTITUTE OF TECHNOLOGY VENDOR DETAILS:")
        print("=" * 65)
        for acc in created_accounts:
            print(f"  Name:     {acc['name']}")
            print(f"  Email:    {acc['email']}")
            print(f"  Password: {acc['password']}")
            print(f"  Canteen:  {acc['canteen']}")
            print(f"  College:  {acc['college']}")
            print(f"  Role:     {acc['role']}")
            print("-" * 65)

if __name__ == "__main__":
    asyncio.run(create_scient_vendors())
