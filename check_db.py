import asyncio
from app.database import AsyncSessionLocal
from app.models import User, Category, MenuItem, KitchenSettings, FaqCategory

async def main():
    async with AsyncSessionLocal() as db:
        from sqlalchemy.future import select
        
        # Check users
        users = (await db.execute(select(User))).scalars().all()
        print(f"Users in DB ({len(users)}):")
        for u in users:
            print(f" - {u.name} ({u.email})")
            
        # Check categories
        categories = (await db.execute(select(Category))).scalars().all()
        print(f"\nCategories in DB ({len(categories)}):")
        cat_map = {}
        for c in categories:
            cat_map[c.id] = c.name
            print(f" - {c.name} (ID: {c.id})")
            
        # Check menu items
        menu_items = (await db.execute(select(MenuItem))).scalars().all()
        print(f"\nMenu Items in DB ({len(menu_items)}):")
        for m in menu_items:
            cat_name = cat_map.get(m.category_id, "Unknown")
            print(f" - {m.name} (${m.price}) | Category: {cat_name} (ID: {m.category_id})")
            
        # Check kitchen settings
        settings = (await db.execute(select(KitchenSettings))).scalars().first()
        print(f"\nKitchen Settings: is_accepting_orders={settings.is_accepting_orders}, max={settings.max_concurrent_orders}")

if __name__ == "__main__":
    asyncio.run(main())
