import asyncio
import re
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.database import Base
from app.config import settings
from alembic.config import Config
from alembic import command

async def ensure_db_exists():
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
        
    # Split to get base url and database name
    base_url, db_name = db_url.rsplit("/", 1)
    if "?" in db_name:
        db_name_clean, query_params = db_name.split("?", 1)
        postgres_url = f"{base_url}/postgres?{query_params}"
    else:
        db_name_clean = db_name
        postgres_url = f"{base_url}/postgres"
        
    # Sanitize database name to prevent syntax issues
    db_name_clean = re.sub(r'[^a-zA-Z0-9_]', '', db_name_clean)
    
    print(f"Checking if database '{db_name_clean}' exists...")
    temp_engine = create_async_engine(postgres_url, isolation_level="AUTOCOMMIT")
    try:
        async with temp_engine.connect() as conn:
            result = await conn.execute(text(
                f"SELECT 1 FROM pg_database WHERE datname = '{db_name_clean}';"
            ))
            exists = result.scalar() is not None
            if not exists:
                print(f"Database '{db_name_clean}' not found. Creating it...")
                await conn.execute(text(f"CREATE DATABASE {db_name_clean};"))
                print(f"Database '{db_name_clean}' created successfully.")
            else:
                print(f"Database '{db_name_clean}' already exists.")
    except Exception as e:
        print(f"Warning during database check/creation: {e}")
    finally:
        await temp_engine.dispose()

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
    print("Connecting to database server...")
    
    # 1. First ensure database exists (connects to default 'postgres' database first)
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(ensure_db_exists())
        # 2. Check tables and create fresh if needed
        is_fresh = loop.run_until_complete(check_and_create_fresh())
    finally:
        loop.close()
        
    # 3. Now run Alembic synchronously (no event loop active here)
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
