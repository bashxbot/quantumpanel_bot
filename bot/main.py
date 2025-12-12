import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from loguru import logger

from bot.config import config
from bot.database import init_db, async_session
from bot.services.cache import cache
from bot.services.admin_service import AdminService
from bot.handlers import user, admin


logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
)
logger.add(
    "logs/bot.log",
    rotation="1 day",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG"
)


async def on_startup(bot: Bot):
    logger.info("🚀 Starting Quantum Panel Bot...")
    
    await init_db()
    
    from bot.migrate_banned import migrate as migrate_banned
    await migrate_banned()
    
    await cache.connect()
    
    async with async_session() as session:
        admin_service = AdminService(session)
        await admin_service.ensure_root_admin()
    
    bot_info = await bot.get_me()
    logger.info(f"✅ Bot started: @{bot_info.username}")


async def on_shutdown(bot: Bot):
    logger.info("🛑 Shutting down bot...")
    await cache.disconnect()
    logger.info("👋 Bot stopped")


async def main():
    if not config.bot.token:
        logger.error("❌ BOT_TOKEN not found in environment variables!")
        sys.exit(1)
    
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    dp.include_router(user.router)
    dp.include_router(admin.router)
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    logger.info("📡 Starting polling...")
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
