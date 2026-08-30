"""
Concurrent Load Test: Create N users → add to cart → place orders simultaneously.

This script:
  1. Creates a custom number of test users directly in the database
     (bypasses OTP verification since WhatsApp isn't available in tests).
  2. Logs in each user to get JWT tokens.
  3. Every user adds the SAME menu item(s) to their cart.
  4. ALL users place their order at the exact same time using asyncio.gather().

Usage:
    python load_test.py                  # default: 5 users
    python load_test.py --users 20       # 20 concurrent users
    python load_test.py --users 10 --item "Chicken Biryani"

Requires: PostgreSQL running, database seeded (run the server once first).
"""

import argparse
import asyncio
import hashlib
import json
import os
import sys
import time
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Disable order cooldown for load testing
os.environ["ORDER_COOLDOWN_SECONDS"] = "0"

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import AsyncSessionLocal, engine
from app.models import User, College, Canteen
from app.security import hash_password, create_access_token
from sqlalchemy.future import select

# ─── Config ────────────────────────────────────────────────────
APP_KEY_HEADER = {"X-App-Key": "ONFOOD_SECURE_CLIENT_APP_KEY_2026"}
TEST_PASSWORD_RAW = "loadtest_password_2026"
TEST_PASSWORD_HASH = hashlib.sha256(TEST_PASSWORD_RAW.encode()).hexdigest()


# ─── Pretty Print ──────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    GREY   = "\033[90m"
    BLUE   = "\033[94m"
    MAGENTA= "\033[95m"

def banner(text):
    w = len(text) + 6
    print(f"\n{C.CYAN}{'=' * w}")
    print(f"||  {C.BOLD}{text}{C.RESET}{C.CYAN}  ||")
    print(f"{'=' * w}{C.RESET}")

def ok(msg):
    print(f"  {C.GREEN}[OK]{C.RESET} {msg}")

def fail(msg):
    print(f"  {C.RED}[FAIL]{C.RESET} {msg}")

def info(msg):
    print(f"  {C.GREY}->{C.RESET} {msg}")


# Precompute bcrypt hash ONCE at module load (saves 150ms per user = ~2 minutes for 650 users!)
PRECOMPUTED_PASSWORD_HASH = hash_password(TEST_PASSWORD_HASH)


# ─── Step 1: Create test users directly in DB ─────────────────
async def create_test_users(num_users: int) -> list[dict]:
    """Bulk create/update N test users in the database quickly."""
    users = []

    async with AsyncSessionLocal() as db:
        # Get the first college and its canteen for assigning to users
        college = (await db.execute(select(College).limit(1))).scalar_one_or_none()
        if not college:
            fail("No colleges found in database. Run the server once to seed data.")
            sys.exit(1)

        # Get a canteen linked to this college
        canteen = (await db.execute(
            select(Canteen).join(Canteen.colleges).where(
                College.id == college.id,
                Canteen.is_active == True,
            ).limit(1)
        )).scalar_one_or_none()
        if not canteen:
            fail("No active canteen found. Run the server once to seed data.")
            sys.exit(1)

        info(f"College: {college.name} | Canteen: {canteen.name}")

        # Clean up old test orders so they don't count towards kitchen capacity
        from app.models import Order, OrderStatus, KitchenSettings, MenuItem
        from sqlalchemy import update

        # Ensure kitchen capacity is at least num_users + 100
        ks = (await db.execute(select(KitchenSettings).where(KitchenSettings.id == 1))).scalar_one_or_none()
        if ks:
            ks.is_accepting_orders = True
            ks.max_concurrent_orders = max(ks.max_concurrent_orders or 20, num_users + 100)
        else:
            db.add(KitchenSettings(id=1, base_prep_buffer_minutes=3, max_concurrent_orders=max(50, num_users + 100), is_accepting_orders=True))

        # Replenish stock for all menu items
        await db.execute(update(MenuItem).values(stock=max(2000, num_users * 3), is_available=True))

        # Mark previous active test orders as DELIVERED
        await db.execute(
            update(Order)
            .where(
                Order.status.in_([OrderStatus.PLACED, OrderStatus.PREPARING]),
                Order.notes.ilike("%Load test order%")
            )
            .values(status=OrderStatus.DELIVERED)
        )

        # 1-query fetch for all existing test users (much faster than N queries)
        existing_result = await db.execute(
            select(User).where(User.email.like("loadtest_user_%"))
        )
        existing_map = {u.email: u for u in existing_result.scalars().all()}

        for i in range(1, num_users + 1):
            email = f"loadtest_user_{i}@test.local"
            roll  = f"LT{i:04d}"

            existing = existing_map.get(email)
            if existing:
                existing.phone = f"91900000{i:04d}"
                existing.phone_verified = True
                existing.college = college.name
                existing.college_id = college.id
                existing.preferred_canteen_id = canteen.id
                existing.roll_number = roll
                existing.hashed_password = PRECOMPUTED_PASSWORD_HASH
                existing.last_order_at = None
                existing.token_version = 1
                existing.refresh_token_version = 1
                user_obj = existing
            else:
                user_obj = User(
                    name=f"Load Test User {i}",
                    email=email,
                    phone=f"91900000{i:04d}",
                    phone_verified=True,
                    roll_number=roll,
                    college=college.name,
                    college_id=college.id,
                    preferred_canteen_id=canteen.id,
                    hashed_password=PRECOMPUTED_PASSWORD_HASH,
                )
                db.add(user_obj)

            users.append(user_obj)

        # Single bulk commit for all users
        await db.commit()

        # Format user dicts
        user_dicts = [
            {
                "id": str(u.id),
                "email": u.email,
                "name": u.name,
                "roll": u.roll_number,
            }
            for u in users
        ]

    return user_dicts


# ─── Step 2: Login all users ──────────────────────────────────
async def login_user(client: AsyncClient, email: str) -> dict | None:
    """Login a single user, return token + user data or None on failure."""
    res = await client.post("/api/auth/login", json={
        "email": email,
        "password": TEST_PASSWORD_HASH,
    })
    if res.status_code == 200:
        data = res.json()
        return {
            "token": data["accessToken"],
            "user_id": data["user"]["id"],
            "email": email,
        }
    return None


# ─── Step 3: Single user flow (cart + order) ──────────────────
async def user_order_flow(
    client: AsyncClient,
    user_info: dict,
    menu_items: list[dict],
    user_number: int,
    ready_event: asyncio.Event,
) -> dict:
    """
    For one user:
      1. Clear cart
      2. Add the target menu items to cart
      3. Wait for the synchronization event (so all users order at the same time)
      4. Place the order

    Returns a result dict with timing and status info.
    """
    token = user_info["token"]
    headers = {**APP_KEY_HEADER, "Authorization": f"Bearer {token}"}
    result = {
        "user": user_info["email"],
        "user_number": user_number,
        "cart_ok": False,
        "order_ok": False,
        "order_id": None,
        "pickup_number": None,
        "status": None,
        "error": None,
        "order_time_ms": 0,
    }

    try:
        # 1. Clear cart
        await client.delete("/api/cart", headers=headers)

        # 2. Add items to cart
        for item in menu_items:
            add_res = await client.post("/api/cart/items", headers=headers, json={
                "menuItemId": item["id"],
                "quantity": 1,
            })
            if add_res.status_code not in (200, 201):
                result["error"] = f"Failed to add {item['name']} to cart: {add_res.status_code}"
                return result

        # 3. Validate cart to get the correct total
        validate_res = await client.post("/api/cart/validate", headers=headers)
        if validate_res.status_code != 200:
            result["error"] = f"Cart validation failed: {validate_res.status_code}"
            return result

        cart_total = validate_res.json()["currentTotal"]
        result["cart_ok"] = True

        # 4. Wait for the GO signal — all users fire simultaneously
        await ready_event.wait()

        # 5. Place order (timed)
        t0 = time.perf_counter()
        order_res = await client.post("/api/orders", headers=headers, json={
            "totalAmount": float(cart_total),
            "notes": f"Load test order from user #{user_number}",
        })
        t1 = time.perf_counter()
        result["order_time_ms"] = round((t1 - t0) * 1000, 1)

        if order_res.status_code == 201:
            order_data = order_res.json()
            result["order_ok"] = True
            result["order_id"] = order_data["id"]
            result["pickup_number"] = order_data.get("pickupNumber")
            result["status"] = order_data.get("status")
        else:
            body = order_res.json() if order_res.headers.get("content-type", "").startswith("application/json") else {}
            result["error"] = body.get("message", f"HTTP {order_res.status_code}")

    except Exception as e:
        result["error"] = str(e)

    return result


# ─── Main ─────────────────────────────────────────────────────
async def run_load_test(num_users: int, item_name: str | None, api_url: str | None = None, app_key: str | None = None):
    banner(f"OnFood Load Test - {num_users} concurrent users")

    target_headers = {
        "X-App-Key": app_key or APP_KEY_HEADER["X-App-Key"],
        "Content-Type": "application/json",
    }

    if api_url:
        target_url = api_url.rstrip("/")
        info(f"Target API Server: {target_url}")
        client_kwargs = {
            "base_url": target_url,
            "headers": target_headers,
            "timeout": 120.0,
        }
    else:
        info("Target API Server: In-process ASGI Transport (direct)")
        client_kwargs = {
            "transport": ASGITransport(app=app),
            "base_url": "http://loadtest",
            "headers": target_headers,
            "timeout": 120.0,
        }

    # ── 1. Create users ──────────────────────────────────
    info("Creating test users in database...")
    t0 = time.perf_counter()
    users = await create_test_users(num_users)
    ok(f"Created {len(users)} test users in {time.perf_counter() - t0:.1f}s")

    async with AsyncClient(**client_kwargs) as client:
        # ── 2. Generate auth tokens directly (bypass login rate limiter) ──
        info("Generating auth tokens for all users...")
        t0 = time.perf_counter()
        logged_in = []
        for u in users:
            token = create_access_token(user_id=u["id"], role="customer")
            logged_in.append({
                "token": token,
                "user_id": u["id"],
                "email": u["email"],
            })
        elapsed = time.perf_counter() - t0
        ok(f"Generated tokens for {len(logged_in)} users in {elapsed:.3f}s")

        # ── 3. Discover menu items ───────────────────────
        info("Fetching menu...")
        menu_res = await client.get("/api/menu")
        if menu_res.status_code != 200:
            fail(f"Failed to fetch menu from {menu_res.url}: {menu_res.status_code} - {menu_res.text}")
            return
        all_items = menu_res.json()

        if item_name:
            target_items = [
                i for i in all_items
                if item_name.lower() in i["name"].lower() and i.get("isAvailable", True)
            ]
            if not target_items:
                fail(f"No available menu item matching '{item_name}' found.")
                info("Available items: " + ", ".join(i["name"] for i in all_items[:10]))
                return
        else:
            # Pick the first available item
            target_items = [i for i in all_items if i.get("isAvailable", True)][:1]
            if not target_items:
                fail("No available menu items found.")
                return

        items_desc = ", ".join(f"{i['name']} (Rs.{i['price']})" for i in target_items)
        ok(f"Target order: {items_desc}")

        # ── 4. Run concurrent order flow ─────────────────
        banner(f"Firing {len(logged_in)} orders simultaneously...")

        ready_event = asyncio.Event()

        # Create all user tasks (they will each add to cart and then wait)
        order_tasks = [
            user_order_flow(client, u, target_items, idx + 1, ready_event)
            for idx, u in enumerate(logged_in)
        ]

        # Start all tasks (they will add to cart then wait for the event)
        gathered = asyncio.gather(*order_tasks)

        # Small delay to let all coroutines reach the wait point
        await asyncio.sleep(0.3)

        # Fire! All users place their order simultaneously
        t_start = time.perf_counter()
        ready_event.set()

        results = await gathered
        t_total = time.perf_counter() - t_start

        # ── 5. Report results ────────────────────────────
        banner("Results")

        successes = [r for r in results if r["order_ok"]]
        failures  = [r for r in results if not r["order_ok"]]

        for r in results:
            tag = f"User #{r['user_number']:>3}"
            if r["order_ok"]:
                ok(f"{tag}  Pickup #{r['pickup_number']:<4}  "
                   f"{r['status']:<10}  {r['order_time_ms']:>7.1f}ms  "
                   f"{C.GREY}{r['order_id'][:8]}..{C.RESET}")
            else:
                fail(f"{tag}  {C.RED}{r['error']}{C.RESET}")

        # Summary
        print()
        print(f"  {C.CYAN}{'-' * 56}{C.RESET}")
        print(f"  {C.BOLD}Total users:{C.RESET}    {num_users}")
        print(f"  {C.GREEN}Successful:{C.RESET}     {len(successes)}")
        print(f"  {C.RED}Failed:{C.RESET}         {len(failures)}")

        if successes:
            times = [r["order_time_ms"] for r in successes]
            print(f"  {C.BOLD}Order times:{C.RESET}")
            print(f"    Min:     {min(times):>8.1f} ms")
            print(f"    Max:     {max(times):>8.1f} ms")
            print(f"    Avg:     {sum(times)/len(times):>8.1f} ms")
            print(f"    Total:   {t_total*1000:>8.1f} ms")

        pickups = [r["pickup_number"] for r in successes if r["pickup_number"] is not None]
        if pickups:
            print(f"  {C.BOLD}Pickup numbers:{C.RESET} {', '.join(f'#{p}' for p in sorted(pickups))}")

        print(f"  {C.CYAN}{'-' * 56}{C.RESET}")

        if failures:
            print(f"\n  {C.YELLOW}Failure breakdown:{C.RESET}")
            error_counts: dict[str, int] = {}
            for r in failures:
                err = r.get("error", "Unknown")
                error_counts[err] = error_counts.get(err, 0) + 1
            for err, count in error_counts.items():
                print(f"    {C.RED}x{count}{C.RESET}  {err}")

    # Cleanup engine
    await engine.dispose()


def main():
    parser = argparse.ArgumentParser(
        description="OnFood Load Test: create N users and place orders simultaneously."
    )
    parser.add_argument(
        "--users", "-n",
        type=int,
        default=5,
        help="Number of concurrent users to simulate (default: 5)",
    )
    parser.add_argument(
        "--item", "-i",
        type=str,
        default=None,
        help="Menu item name to order (partial match). If omitted, uses the first available item.",
    )
    parser.add_argument(
        "--url", "-u",
        type=str,
        default=None,
        help="Target API server URL (e.g., http://localhost:8000 or https://api1.krtech.online). If omitted, uses in-process ASGI app.",
    )
    parser.add_argument(
        "--app-key", "-k",
        type=str,
        default=None,
        help="X-App-Key header value (default: ONFOOD_SECURE_CLIENT_APP_KEY_2026)",
    )
    args = parser.parse_args()

    if args.users < 1:
        print("Error: --users must be at least 1")
        sys.exit(1)

    asyncio.run(run_load_test(args.users, args.item, args.url, args.app_key))


if __name__ == "__main__":
    main()

