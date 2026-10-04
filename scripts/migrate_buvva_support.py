import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from sqlalchemy import text

MIGRATIONS = [
    # 1. users: avatar & gender
    """
    ALTER TABLE users 
    ADD COLUMN IF NOT EXISTS avatar VARCHAR(50) DEFAULT 'default',
    ADD COLUMN IF NOT EXISTS gender VARCHAR(20) DEFAULT NULL;
    """,
    # 2. colleges: photo_url, map_url, latitude, longitude
    """
    ALTER TABLE colleges
    ADD COLUMN IF NOT EXISTS photo_url TEXT DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS map_url TEXT DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION DEFAULT NULL;
    """,
    # 3. canteens: photo_url, map_url, location_description, latitude, longitude
    """
    ALTER TABLE canteens
    ADD COLUMN IF NOT EXISTS photo_url TEXT DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS map_url TEXT DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS location_description TEXT DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION DEFAULT NULL;
    """,
    # 4. support_tickets: order_id & updated_at
    """
    ALTER TABLE support_tickets
    ADD COLUMN IF NOT EXISTS order_id UUID DEFAULT NULL REFERENCES orders(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    """,
    # 5. support_messages table
    """
    CREATE TABLE IF NOT EXISTS support_messages (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        ticket_id UUID NOT NULL REFERENCES support_tickets(id) ON DELETE CASCADE,
        sender_type VARCHAR(20) NOT NULL,
        sender_id VARCHAR(64) NOT NULL,
        sender_name VARCHAR(100) DEFAULT 'Support',
        message TEXT NOT NULL,
        channel VARCHAR(20) DEFAULT 'APP',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,
    # 6. Index on support_messages.ticket_id
    """
    CREATE INDEX IF NOT EXISTS idx_support_messages_ticket ON support_messages(ticket_id);
    """
]

async def run_migrations():
    async with engine.begin() as conn:
        for stmt in MIGRATIONS:
            print(f"Executing: {stmt.strip()[:60]}...")
            await conn.execute(text(stmt))
    print("All migrations completed successfully!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_migrations())
