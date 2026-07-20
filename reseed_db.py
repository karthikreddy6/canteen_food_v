import asyncio
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models import Category, MenuItem, FaqCategory, FaqItem
from app.main import seed_database

async def clean_and_reseed():
    async with AsyncSessionLocal() as db:
        # Delete old menu items and categories
        print("Cleaning up old database entries...")
        await db.execute(select(MenuItem)) # just warm up
        
        from app.models import Order, OrderItem, CartItem, Banner, VendorAccount, College, Canteen, User, SupportTicket, StaffMember, college_canteens
        from sqlalchemy import delete
        
        # Delete order-related tables first to prevent constraint violations
        await db.execute(delete(OrderItem))
        await db.execute(delete(Order))
        await db.execute(delete(CartItem))
        await db.execute(delete(FaqItem))
        await db.execute(delete(FaqCategory))
        await db.execute(delete(Banner))
        await db.execute(delete(VendorAccount))
        await db.execute(delete(StaffMember))
        await db.execute(delete(SupportTicket))
        await db.execute(delete(User))
        await db.execute(delete(MenuItem))
        await db.execute(delete(Category))
        await db.execute(delete(college_canteens))
        await db.execute(delete(Canteen))
        await db.execute(delete(College))
        
        await db.commit()
        print("Database cleaned.")
        
    # Run seeder to populate everything fresh
    print("Running main database seeder...")
    await seed_database()
    print("Database seeding complete!")

if __name__ == "__main__":
    asyncio.run(clean_and_reseed())
