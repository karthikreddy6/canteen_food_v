import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.database import Base
from app.config import settings
from alembic.config import Config
from alembic import command

async def check_and_create_fresh():
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
        
    engine = create_async_engine(db_url)
    
    # Check if 'users' table exists
    async with engine.connect() as conn:
        result = await conn.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users');"
        ))
        users_table_exists = result.scalar()
        
    is_fresh = False
    if not users_table_exists:
        is_fresh = True
        print("Fresh database detected. Creating all tables from SQLAlchemy models...")
        async with engine.begin() as conn:
            import app.models
            await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")
        
    await engine.dispose()
    return is_fresh

def main():
    print("Connecting to database...")
    
    # Run database checks in a separate event loop
    loop = asyncio.new_event_loop()
    try:
        is_fresh = loop.run_until_complete(check_and_create_fresh())
    finally:
        loop.close()
        
    # Now run Alembic synchronously (no event loop active here, so env.py can start its own)
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
        
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    
    if is_fresh:
        print("Stamping database with latest Alembic revision (stamp head)...")
        command.stamp(alembic_cfg, "head")
        print("Alembic stamped successfully.")
    else:
        print("Existing database detected. Running alembic migrations (upgrade head)...")
        command.upgrade(alembic_cfg, "head")
        print("Alembic migrations completed successfully.")
        
    print("Database initialization complete!")

if __name__ == "__main__":
    main()
