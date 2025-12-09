from typing import Optional, List, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from dataclasses import dataclass

from bot.models import TrustedSeller
from bot.services.cache import cache


@dataclass
class SellerData:
    id: int
    username: str
    name: Optional[str]
    description: Optional[str]
    platforms: Optional[str] = None
    country: Optional[str] = None
    is_active: bool = False


class SellerService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_sellers(self) -> List[SellerData]:
        cache_key = "sellers:all"
        cached = await cache.get(cache_key)
        
        if cached:
            return [SellerData(**s) for s in cached]
        
        stmt = select(TrustedSeller).order_by(TrustedSeller.created_at.desc())
        result = await self.session.execute(stmt)
        sellers = list(result.scalars().all())
        
        sellers_data = [
            SellerData(
                id=s.id,
                username=s.username,
                name=s.name,
                description=s.description,
                platforms=s.platforms,
                country=s.country,
                is_active=s.is_active
            )
            for s in sellers
        ]
        
        await cache.set(cache_key, [
            {"id": s.id, "username": s.username, "name": s.name, "description": s.description,
             "platforms": s.platforms, "country": s.country, "is_active": s.is_active}
            for s in sellers_data
        ], expire=300)
        
        return sellers_data
    
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
