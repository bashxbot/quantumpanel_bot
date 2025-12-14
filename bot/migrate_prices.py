"""
Migration script to change product_prices.price and users.balance columns from INTEGER to NUMERIC
This migration runs automatically on bot startup.

Usage: python -m bot.migrate_prices
"""
import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from loguru import logger

async def migrate():
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        logger.warning("⚠️ DATABASE_URL not set, skipping price migration")
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
        # Migrate product_prices.price column
        result = await conn.execute(text("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'product_prices' AND column_name = 'price'
        """))
        row = result.fetchone()
        
        if row:
            current_type = row[0].lower()
            if 'int' in current_type or 'double' in current_type or 'float' in current_type or 'real' in current_type:
                logger.info(f"📊 product_prices.price: {current_type}, migrating to NUMERIC(10,2)...")
                await conn.execute(text("""
                    ALTER TABLE product_prices 
                    ALTER COLUMN price TYPE NUMERIC(10,2) USING price::numeric(10,2)
                """))
                logger.info("✅ product_prices.price now supports decimals.")
            elif 'numeric' in current_type:
                logger.debug(f"✅ product_prices.price already supports decimals (type: {current_type})")
            else:
                logger.debug(f"✅ product_prices.price type: {current_type}")
        else:
            logger.debug("⚠️ Table 'product_prices' not found. Will be created on next bot start.")
        
        # Migrate users.balance column
        result = await conn.execute(text("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'balance'
        """))
        row = result.fetchone()
        
        if row:
            current_type = row[0].lower()
            if 'int' in current_type or 'double' in current_type or 'float' in current_type or 'real' in current_type:
                logger.info(f"📊 users.balance: {current_type}, migrating to NUMERIC(10,2)...")
                await conn.execute(text("""
                    UPDATE users SET balance = 99999999.99 WHERE balance > 99999999.99
                """))
                await conn.execute(text("""
                    ALTER TABLE users 
                    ALTER COLUMN balance TYPE NUMERIC(10,2) USING balance::numeric(10,2)
                """))
                logger.info("✅ users.balance now supports decimals.")
            elif 'numeric' in current_type:
                logger.debug(f"✅ users.balance already supports decimals (type: {current_type})")
            else:
                logger.debug(f"✅ users.balance type: {current_type}")
        else:
            logger.debug("⚠️ Table 'users' not found. Will be created on next bot start.")
    
    await engine.dispose()
    logger.info("✅ Price/balance migration check complete!")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(migrate())
