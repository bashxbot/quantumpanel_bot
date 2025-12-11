"""
Migration script to change product_prices.price column from INTEGER to FLOAT/REAL
Run this script once to migrate existing databases.

Usage: python -m bot.migrate_prices
"""
import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def migrate():
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        print("❌ DATABASE_URL not set")
        return
    
    # Convert to async URL
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Remove sslmode if present
    if "sslmode=" in database_url:
        database_url = database_url.replace("sslmode=disable", "").replace("sslmode=require", "")
        database_url = database_url.replace("?&", "?").replace("&&", "&")
        if database_url.endswith("?") or database_url.endswith("&"):
            database_url = database_url[:-1]
    
    engine = create_async_engine(database_url)
    
    async with engine.begin() as conn:
        # Check if column needs migration
        result = await conn.execute(text("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'product_prices' AND column_name = 'price'
        """))
        row = result.fetchone()
        
        if row:
            current_type = row[0].lower()
            if 'int' in current_type:
                print(f"📊 Current type: {current_type}, migrating to REAL...")
                await conn.execute(text("""
                    ALTER TABLE product_prices 
                    ALTER COLUMN price TYPE REAL USING price::real
                """))
                print("✅ Migration complete! Price column now supports decimals.")
            else:
                print(f"✅ Column already supports decimals (type: {current_type})")
        else:
            print("⚠️ Table 'product_prices' not found. Will be created on next bot start.")
    
    await engine.dispose()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(migrate())
