import asyncio
import json
import sys
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import text
from app.database import engine
JSON_PATH = BASE_DIR / "app" / "static" / "images" / "indian_dishes_images.json"
SQL_OUTPUT_PATH = BASE_DIR / "scripts" / "insert_indian_dishes.sql"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS indian_dishes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item VARCHAR(255) NOT NULL UNIQUE,
    region VARCHAR(100),
    description TEXT,
    vegetarian_or_non_vegetarian VARCHAR(100),
    dish_type VARCHAR(100),
    image_filename VARCHAR(255),
    image_url TEXT,
    source_page TEXT,
    local_image_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""

def generate_sql_file(data):
    lines = [
        "-- Auto-generated SQL insert script for Indian Dishes",
        CREATE_TABLE_SQL.strip(),
        ""
    ]
    for d in data:
        item = (d.get("item") or "").replace("'", "''")
        region = (d.get("region") or "").replace("'", "''")
        desc = (d.get("description") or "").replace("'", "''")
        veg = (d.get("vegetarian_or_non_vegetarian") or "").replace("'", "''")
        dtype = (d.get("dish_type") or "").replace("'", "''")
        img_fn = (d.get("image_filename") or "").replace("'", "''")
        img_url = (d.get("image_url") or "").replace("'", "''")
        src_page = (d.get("source_page") or "").replace("'", "''")
        fn = d.get("image_filename") or ""
        encoded_fn = urllib.parse.quote(fn)
        local_url = f"/images/{encoded_fn}".replace("'", "''") if fn else ""

        sql = f"""INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
VALUES ('{item}', '{region}', '{desc}', '{veg}', '{dtype}', '{img_fn}', '{img_url}', '{src_page}', '{local_url}')
ON CONFLICT (item) DO UPDATE SET
    region = EXCLUDED.region,
    description = EXCLUDED.description,
    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
    dish_type = EXCLUDED.dish_type,
    image_filename = EXCLUDED.image_filename,
    image_url = EXCLUDED.image_url,
    source_page = EXCLUDED.source_page,
    local_image_url = EXCLUDED.local_image_url;"""
        lines.append(sql)

    SQL_OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated standalone SQL script: {SQL_OUTPUT_PATH.name}")

async def import_to_postgres(data):
    print("Connecting to PostgreSQL using project settings...")
    try:
        async with engine.begin() as conn:
            await conn.execute(text(CREATE_TABLE_SQL))
            
            insert_stmt = text("""
                INSERT INTO indian_dishes (item, region, description, vegetarian_or_non_vegetarian, dish_type, image_filename, image_url, source_page, local_image_url)
                VALUES (:item, :region, :description, :vegetarian_or_non_vegetarian, :dish_type, :image_filename, :image_url, :source_page, :local_image_url)
                ON CONFLICT (item) DO UPDATE SET
                    region = EXCLUDED.region,
                    description = EXCLUDED.description,
                    vegetarian_or_non_vegetarian = EXCLUDED.vegetarian_or_non_vegetarian,
                    dish_type = EXCLUDED.dish_type,
                    image_filename = EXCLUDED.image_filename,
                    image_url = EXCLUDED.image_url,
                    source_page = EXCLUDED.source_page,
                    local_image_url = EXCLUDED.local_image_url;
            """)

            params = []
            for d in data:
                fn = d.get("image_filename") or ""
                params.append({
                    "item": d.get("item") or "",
                    "region": d.get("region") or "",
                    "description": d.get("description") or "",
                    "vegetarian_or_non_vegetarian": d.get("vegetarian_or_non_vegetarian") or "",
                    "dish_type": d.get("dish_type") or "",
                    "image_filename": fn,
                    "image_url": d.get("image_url") or "",
                    "source_page": d.get("source_page") or "",
                    "local_image_url": f"/images/{urllib.parse.quote(fn)}" if fn else ""
                })

            await conn.execute(insert_stmt, params)
            print(f"Successfully inserted/updated {len(params)} dishes into PostgreSQL 'indian_dishes' table!")
    except Exception as e:
        print(f"PostgreSQL connection note: {e}")
        print("When your PostgreSQL service is running, you can run: python scripts/import_indian_dishes.py")

def main():
    if not JSON_PATH.exists():
        print(f"Error: JSON file not found at {JSON_PATH}")
        return

    with open(JSON_PATH, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} items from {JSON_PATH.name}.")
    generate_sql_file(data)
    asyncio.run(import_to_postgres(data))

if __name__ == "__main__":
    main()
