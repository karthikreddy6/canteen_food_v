import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(text("COMMIT")) # Finish implicit transaction
            await db.execute(text("ALTER TYPE order_status ADD VALUE 'SCHEDULED'"))
            print("Successfully added 'SCHEDULED' to order_status enum in PostgreSQL.")
        except Exception as e:
            print(f"Adding 'SCHEDULED' skipped or failed: {e}")
        await db.commit()

if __name__ == "__main__":
    asyncio.run(main())
