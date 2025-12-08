from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime
from loguru import logger

from bot.models import Order, User, Product
from bot.services.cache import cache


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_order(
        self,
        user_id: int,
        product_id: int,
        product_name: str,
        duration: str,
        price: float,
        key_value: Optional[str] = None
    ) -> Order:
        order = Order(
            user_id=user_id,
            product_id=product_id,
            product_name=product_name,
            duration=duration,
            price=price,
            key_value=key_value,
            purchased_at=datetime.utcnow()
        )
        self.session.add(order)
        
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            user.last_purchase_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(order)
        await cache.invalidate_pattern("orders:*")
        logger.info(f"📦 Order created: {order.id} for user {user_id}")
        return order
    
    async def get_user_orders(self, user_id: int, limit: int = 10) -> List[Order]:
        stmt = select(Order).where(
            Order.user_id == user_id
        ).order_by(Order.purchased_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_all_orders(self, limit: int = 100) -> List[Order]:
        stmt = select(Order).options(
            selectinload(Order.user)
        ).order_by(Order.purchased_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_total_revenue(self) -> float:
        stmt = select(func.sum(Order.price))
        result = await self.session.execute(stmt)
        total = result.scalar()
        return float(total) if total else 0.0
    
    async def get_orders_count(self) -> int:
        stmt = select(func.count(Order.id))
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def get_user_orders_count(self, user_id: int) -> int:
        stmt = select(func.count(Order.id)).where(Order.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0
