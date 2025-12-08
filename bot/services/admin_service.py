from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from bot.models import Admin
from bot.services.cache import cache
from bot.config import config


class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def is_admin(self, telegram_id: int) -> bool:
        cache_key = f"is_admin:{telegram_id}"
        cached = await cache.get(cache_key)
        
        if cached is not None:
            return cached
        
        if telegram_id == config.bot.root_admin_id:
            await cache.set(cache_key, True, expire=600)
            return True
        
        stmt = select(Admin).where(Admin.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        admin = result.scalar_one_or_none()
        
        is_admin = admin is not None
        await cache.set(cache_key, is_admin, expire=600)
        return is_admin
    
    async def is_root_admin(self, telegram_id: int) -> bool:
        return telegram_id == config.bot.root_admin_id
    
    async def add_admin(self, telegram_id: int, username: Optional[str] = None) -> bool:
        existing = await self.get_admin(telegram_id)
        if existing:
            return False
        
        admin = Admin(
            telegram_id=telegram_id,
            username=username,
            is_root=telegram_id == config.bot.root_admin_id
        )
        self.session.add(admin)
        await self.session.commit()
        await cache.delete(f"is_admin:{telegram_id}")
        logger.info(f"👑 New admin added: {telegram_id}")
        return True
    
    async def remove_admin(self, telegram_id: int) -> bool:
        if telegram_id == config.bot.root_admin_id:
            logger.warning(f"⚠️ Cannot remove root admin: {telegram_id}")
            return False
        
        stmt = delete(Admin).where(Admin.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        await cache.delete(f"is_admin:{telegram_id}")
        
        if result.rowcount > 0:
            logger.info(f"🗑️ Admin removed: {telegram_id}")
            return True
        return False
    
    async def get_admin(self, telegram_id: int) -> Optional[Admin]:
        stmt = select(Admin).where(Admin.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_admins(self) -> List[Admin]:
        stmt = select(Admin).order_by(Admin.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def ensure_root_admin(self):
        if config.bot.root_admin_id:
            existing = await self.get_admin(config.bot.root_admin_id)
            if not existing:
                admin = Admin(
                    telegram_id=config.bot.root_admin_id,
                    is_root=True
                )
                self.session.add(admin)
                await self.session.commit()
                logger.info(f"👑 Root admin initialized: {config.bot.root_admin_id}")
