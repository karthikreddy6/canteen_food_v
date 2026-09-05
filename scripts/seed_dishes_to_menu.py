import asyncio
import json
import sys
import urllib.parse
from decimal import Decimal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import select, text
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings
from app.models import Canteen, Category, MenuItem, College, college_canteens

script_engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
ScriptSession = async_sessionmaker(bind=script_engine, class_=AsyncSession, expire_on_commit=False)

JSON_PATH = BASE_DIR / "app" / "static" / "images" / "indian_dishes_images.json"
SQL_OUTPUT_PATH = BASE_DIR / "scripts" / "insert_dishes_into_menu_items.sql"

DEFAULT_CANTEENS = [
    "Central Canteen",
    "Hostel Canteen",
    "MBA Canteen",
    "Food Court Express",
    "Arts Canteen",
    "Science Canteen",
]

def determine_price(dish: dict) -> tuple[Decimal, Decimal]:
    diet = (dish.get("vegetarian_or_non_vegetarian") or "").lower()
    if "non-veg" in diet or "non veg" in diet:
        return Decimal("140.00"), Decimal("160.00")
    elif "sweet" in diet or "dessert" in diet:
        return Decimal("60.00"), Decimal("70.00")
    else:
        return Decimal("90.00"), Decimal("105.00")

async def seed_dishes_to_menu():
    if not JSON_PATH.exists():
        print(f"Error: JSON file not found at {JSON_PATH}")
        return

    with open(JSON_PATH, "r", encoding="utf-8-sig") as f:
        dishes = json.load(f)

    total_dishes = len(dishes)
    print(f"Loaded {total_dishes} dishes from {JSON_PATH.name}")

    async with ScriptSession() as db:
        # 1. Fetch or create active canteens
        result = await db.execute(select(Canteen).where(Canteen.is_active == True).order_by(Canteen.name))
        canteens = list(result.scalars().all())

        if not canteens:
            print("No canteens found in database. Initializing default canteens...")
            for name in DEFAULT_CANTEENS:
                canteen = Canteen(name=name, is_active=True)
                db.add(canteen)
                canteens.append(canteen)
            await db.flush()

        num_canteens = len(canteens)
        print(f"Found {num_canteens} active canteens:")
        for c in canteens:
            print(f"  - {c.name} ({c.id})")

        # 2. Fetch existing categories
        cat_result = await db.execute(select(Category))
        categories_by_name = {c.name: c for c in cat_result.scalars().all()}

        # 3. Fetch existing menu items: key = (canteen_id, name)
        item_result = await db.execute(select(MenuItem))
        existing_items = {(item.canteen_id, item.name): item for item in item_result.scalars().all()}

        # 4. Process each dish:
        # - Make each dish item a Category
        # - Equally divide items across all canteens using round-robin
        canteen_counts = {c.name: 0 for c in canteens}
        display_order_counter = len(categories_by_name) + 1

        for i, dish in enumerate(dishes):
            item_name = dish.get("item", "").strip()
            if not item_name:
                continue

            image_fn = dish.get("image_filename", "")
            local_image_url = f"/images/{urllib.parse.quote(image_fn)}" if image_fn else None
            description = dish.get("description", "") or f"{item_name} - authentic Indian preparation."
            price, orig_price = determine_price(dish)
            discount = round(((orig_price - price) / orig_price) * Decimal("100"), 2)

            # A. Ensure Category exists for this item
            category = categories_by_name.get(item_name)
            if not category:
                category = Category(
                    name=item_name,
                    icon_url=local_image_url,
                    display_order=display_order_counter,
                    is_active=True,
                )
                display_order_counter += 1
                db.add(category)
                categories_by_name[item_name] = category
                await db.flush()  # to generate category.id
            else:
                if local_image_url and not category.icon_url:
                    category.icon_url = local_image_url

            # B. Assign to canteen (round-robin: equally divided)
            assigned_canteen = canteens[i % num_canteens]
            canteen_counts[assigned_canteen.name] += 1

            # C. Insert or update MenuItem
            key = (assigned_canteen.id, item_name)
            existing_menu_item = existing_items.get(key)

            if existing_menu_item:
                existing_menu_item.price = price
                existing_menu_item.original_price = orig_price
                existing_menu_item.discount_percent = discount
                existing_menu_item.category_id = category.id
                existing_menu_item.image_url = local_image_url
                existing_menu_item.description = description
                existing_menu_item.is_student_visible = True
                existing_menu_item.is_available = True
            else:
                menu_item = MenuItem(
                    name=item_name,
                    price=price,
                    original_price=orig_price,
                    discount_percent=discount,
                    category_id=category.id,
                    canteen_id=assigned_canteen.id,
                    image_url=local_image_url,
                    description=description,
                    stock=50,
                    is_student_visible=True,
                    special_offer=False,
                    is_available=True,
                    preparation_time_minutes=12,
                )
                db.add(menu_item)
                existing_items[key] = menu_item

        await db.commit()
    await script_engine.dispose()
    print("\n Seeding completed successfully!")
    print(f"Total categories present: {len(categories_by_name)}")
    print("Dishes distributed per canteen:")
    for c_name, count in canteen_counts.items():
        print(f"  - {c_name}: {count} dishes")

def generate_menu_items_sql():
    with open(JSON_PATH, "r", encoding="utf-8-sig") as f:
        dishes = json.load(f)

    lines = [
        "-- Standalone SQL script: Insert categories and equally distribute menu items across canteens",
        "-- Assumes canteens table is populated. Matches canteens by row number / name.",
        ""
    ]

    # Create temporary helper query using SQL
    lines.append("""
DO $$
DECLARE
    canteens_list UUID[];
    num_canteens INT;
    c_idx INT;
    cat_id UUID;
    cant_id UUID;
BEGIN
    -- Collect all active canteen IDs into an array
    SELECT array_agg(id ORDER BY name) INTO canteens_list FROM canteens WHERE is_active = true;
    num_canteens := array_length(canteens_list, 1);

    IF num_canteens IS NULL OR num_canteens = 0 THEN
        RAISE NOTICE 'No active canteens found in database. Please add canteens first.';
        RETURN;
    END IF;
""")

    for idx, dish in enumerate(dishes):
        item_name = (dish.get("item") or "").strip().replace("'", "''")
        if not item_name:
            continue
        image_fn = dish.get("image_filename") or ""
        local_url = f"/images/{urllib.parse.quote(image_fn)}".replace("'", "''") if image_fn else ""
        desc = (dish.get("description") or f"{item_name} - authentic Indian preparation.").replace("'", "''")
        price, orig = determine_price(dish)
        discount = round(((orig - price) / orig) * Decimal("100"), 2)

        sql_block = f"""
    -- Dish {idx + 1}: {item_name}
    -- 1. Ensure category exists
    SELECT id INTO cat_id FROM categories WHERE name = '{item_name}' LIMIT 1;
    IF cat_id IS NULL THEN
        cat_id := gen_random_uuid();
        INSERT INTO categories (id, name, icon_url, display_order, is_active, updated_at)
        VALUES (cat_id, '{item_name}', '{local_url}', {idx + 1}, true, NOW());
    END IF;

    -- 2. Pick assigned canteen (round-robin)
    c_idx := ({idx} % num_canteens) + 1;
    cant_id := canteens_list[c_idx];

    -- 3. Insert or update menu item for that canteen
    IF EXISTS (SELECT 1 FROM menu_items WHERE canteen_id = cant_id AND name = '{item_name}') THEN
        UPDATE menu_items SET
            price = {price},
            original_price = {orig},
            discount_percent = {discount},
            category_id = cat_id,
            image_url = '{local_url}',
            description = '{desc}',
            stock = 50,
            is_student_visible = true,
            is_available = true,
            preparation_time_minutes = 12
        WHERE canteen_id = cant_id AND name = '{item_name}';
    ELSE
        INSERT INTO menu_items (id, name, price, original_price, discount_percent, category_id, canteen_id, image_url, description, stock, is_student_visible, is_special_offer, is_available, preparation_time_minutes)
        VALUES (gen_random_uuid(), '{item_name}', {price}, {orig}, {discount}, cat_id, cant_id, '{local_url}', '{desc}', 50, true, false, true, 12);
    END IF;
"""
        lines.append(sql_block)

    lines.append("""
    RAISE NOTICE 'Menu items and categories inserted and equally distributed successfully!';
END $$;
""")

    SQL_OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated standalone SQL script: {SQL_OUTPUT_PATH.name}")

if __name__ == "__main__":
    generate_menu_items_sql()
    try:
        asyncio.run(seed_dishes_to_menu())
    except Exception as e:
        print(f"\nNote: Direct database connection could not be established right now: {e}")
        print(f"You can run this script once PostgreSQL is started: python scripts/seed_dishes_to_menu.py")
        print(f"Or run the SQL file: {SQL_OUTPUT_PATH.name}")
