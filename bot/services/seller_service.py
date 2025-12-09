from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from bot.models import TrustedSeller
from bot.services.cache import cache


class SellerService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_sellers(self) -> List[TrustedSeller]:
        cache_key = "sellers:all"
        cached = await cache.get(cache_key)
        
        if cached:
            return [TrustedSeller(**s) for s in cached]
        
        stmt = select(TrustedSeller).order_by(TrustedSeller.created_at.desc())
        result = await self.session.execute(stmt)
        sellers = list(result.scalars().all())
        
        await cache.set(cache_key, [
            {"id": s.id, "username": s.username, "name": s.name, "description": s.description}
            for s in sellers
        ], expire=300)
        
        return sellers
    
    async def add_seller(
        self,
        username: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        platforms: Optional[str] = None,
        country: Optional[str] = None
    ) -> TrustedSeller:
        seller = TrustedSeller(
            username=username,
            name=name,
            description=description,
            platforms=platforms,
            country=country
        )
        self.session.add(seller)
        await self.session.commit()
        await self.session.refresh(seller)
        await cache.delete("sellers:all")
        logger.info(f"⭐ Seller added: {username}")
        return seller
    
    async def update_seller(
        self,
        seller_id: int,
        username: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        platforms: Optional[str] = None,
        country: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[TrustedSeller]:
        stmt = select(TrustedSeller).where(TrustedSeller.id == seller_id)
        result = await self.session.execute(stmt)
        seller = result.scalar_one_or_none()
        
        if not seller:
            return None
        
        if username is not None:
            seller.username = username
        if name is not None:
            seller.name = name
        if description is not None:
            seller.description = description
        if platforms is not None:
            seller.platforms = platforms
        if country is not None:
            seller.country = country
        if is_active is not None:
            seller.is_active = is_active
        
        await self.session.commit()
        await self.session.refresh(seller)
        await cache.delete("sellers:all")
        logger.info(f"✏️ Seller updated: {seller_id}")
        return seller
    
    async def remove_seller(self, seller_id: int) -> bool:
        stmt = delete(TrustedSeller).where(TrustedSeller.id == seller_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        await cache.delete("sellers:all")
        
        if result.rowcount > 0:
            logger.info(f"🗑️ Seller removed: {seller_id}")
            return True
        return False
