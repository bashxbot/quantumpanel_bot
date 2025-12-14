from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from decimal import Decimal
from loguru import logger

from bot.models import User, UserStatus
from bot.services.cache import cache


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        cache_key = f"user:{telegram_id}"
        cached = await cache.get(cache_key)
        
        if cached:
            logger.debug(f"📦 User {telegram_id} loaded from cache")
            user = User(**cached)
            return user
        
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            logger.info(f"👤 Creating new user: {telegram_id}")
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        else:
            if user.username != username or user.first_name != first_name:
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                await self.session.commit()
        
        await cache.set(cache_key, {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "balance": user.balance,
            "status": user.status.value,
            "is_reseller": user.is_reseller,
            "is_banned": getattr(user, 'is_banned', False),
        })
        
        return user
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_balance(self, user_id: int, amount: float) -> bool:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            user.balance += Decimal(str(amount))
            await self.session.commit()
            await cache.delete(f"user:{user.telegram_id}")
            logger.info(f"💰 Balance updated for user {user_id}: {amount:+.2f}")
            return True
        return False
    
    async def set_premium(self, user_id: int, is_premium: bool = True) -> bool:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            user.status = UserStatus.PREMIUM if is_premium else UserStatus.FREE
            await self.session.commit()
            await cache.delete(f"user:{user.telegram_id}")
            logger.info(f"⭐ User {user_id} premium status: {is_premium}")
            return True
        return False
    
    async def set_reseller(self, user_id: int, is_reseller: bool = True) -> bool:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            user.is_reseller = is_reseller
            await self.session.commit()
            await cache.delete(f"user:{user.telegram_id}")
            return True
        return False
    
    async def get_all_users(self) -> List[User]:
        stmt = select(User).order_by(User.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_premium_users_count(self) -> int:
        stmt = select(User).where(User.status == UserStatus.PREMIUM)
        result = await self.session.execute(stmt)
        return len(list(result.scalars().all()))
    
    async def get_resellers(self) -> List[User]:
        stmt = select(User).where(User.is_reseller == True).order_by(User.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        clean_username = username.lstrip('@')
        stmt = select(User).where(User.username == clean_username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def set_banned(self, user_id: int, is_banned: bool = True) -> bool:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            user.is_banned = is_banned
            await self.session.commit()
            await cache.delete(f"user:{user.telegram_id}")
            logger.info(f"{'🚫' if is_banned else '✅'} User {user_id} ban status: {is_banned}")
            return True
        return False
    
    async def set_balance(self, user_id: int, amount: float) -> bool:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            user.balance = Decimal(str(amount))
            await self.session.commit()
            await cache.delete(f"user:{user.telegram_id}")
            logger.info(f"💰 Balance set for user {user_id}: {amount}")
            return True
        return False
    
    async def get_premium_users(self) -> List[User]:
        stmt = select(User).where(User.status == UserStatus.PREMIUM).order_by(User.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def remove_premium_by_id(self, user_id: int) -> bool:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            user.status = UserStatus.FREE
            await self.session.commit()
            await cache.delete(f"user:{user.telegram_id}")
            logger.info(f"⭐ Premium removed from user {user_id}")
            return True
        return False
    
    async def set_premium_by_telegram_id(self, telegram_id: int, is_premium: bool = True) -> bool:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            user.status = UserStatus.PREMIUM if is_premium else UserStatus.FREE
            await self.session.commit()
            await cache.delete(f"user:{user.telegram_id}")
            logger.info(f"⭐ User {telegram_id} premium status: {is_premium}")
            return True
        return False
