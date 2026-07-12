import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as db:
        # PostgreSQL doesn't allow ALTER TYPE ADD VALUE inside transactions.
        # But asyncpg / SQLAlchemy manages connection execution context.
        # We can execute them.
        connection = await db.connection()
        print("Altering enum order_status in PostgreSQL...")
        
        # We run it on the connection directly to control commit/transaction boundaries if needed
        # Or we can run them individually committing them.
        try:
            await db.execute(text("COMMIT")) # finish any implicit transaction block
            await db.execute(text("ALTER TYPE order_status ADD VALUE 'PLACED'"))
            print("Successfully added 'PLACED'")
        except Exception as e:
            print(f"Adding 'PLACED' skipped or failed: {e}")
            
        try:
            await db.execute(text("ALTER TYPE order_status ADD VALUE 'READY_FOR_PICKUP'"))
            print("Successfully added 'READY_FOR_PICKUP'")
        except Exception as e:
            print(f"Adding 'READY_FOR_PICKUP' skipped or failed: {e}")
            
        await db.commit()
        print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
