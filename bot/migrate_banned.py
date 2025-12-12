import asyncio
from sqlalchemy import text
from bot.database import engine
from loguru import logger


async def migrate():
    """Add is_banned column to users table if it doesn't exist"""
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'is_banned'
        """))
        exists = result.fetchone()
        
        if not exists:
            logger.info("Adding is_banned column to users table...")
            await conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN is_banned BOOLEAN NOT NULL DEFAULT FALSE
            """))
            logger.info("is_banned column added successfully!")
        else:
            logger.info("is_banned column already exists, skipping migration.")


if __name__ == "__main__":
    asyncio.run(migrate())
