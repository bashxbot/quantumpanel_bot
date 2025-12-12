from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from loguru import logger

from bot.models import Product, ProductPrice, ProductKey
from bot.services.cache import cache


class ProductService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_products(self, active_only: bool = True) -> List[Product]:
        cache_key = f"products:all:{active_only}"
        
        stmt = select(Product).options(selectinload(Product.prices))
        if active_only:
            stmt = stmt.where(Product.is_active == True)
        stmt = stmt.order_by(Product.created_at.desc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_product(self, product_id: int) -> Optional[Product]:
        stmt = select(Product).options(
            selectinload(Product.prices),
            selectinload(Product.keys)
        ).where(Product.id == product_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_product(
        self,
        name: str,
        description: Optional[str] = None,
        image_file_id: Optional[str] = None
    ) -> Product:
        product = Product(
            name=name,
            description=description,
            image_file_id=image_file_id
        )
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        await cache.invalidate_pattern("products:*")
        logger.info(f"📦 Product created: {name}")
        return product
    
    async def update_product(
        self,
        product_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        image_file_id: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Product]:
        product = await self.get_product(product_id)
        if not product:
            return None
        
        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if image_file_id is not None:
            product.image_file_id = image_file_id
        if is_active is not None:
            product.is_active = is_active
        
        await self.session.commit()
        await cache.invalidate_pattern("products:*")
        logger.info(f"📦 Product updated: {product_id}")
        return product
    
    async def delete_product(self, product_id: int) -> bool:
        product = await self.get_product(product_id)
        if not product:
            return False
        
        await self.session.delete(product)
        await self.session.commit()
        await cache.invalidate_pattern("products:*")
        logger.info(f"🗑️ Product deleted with all keys: {product_id}")
        return True
    
    async def add_price(self, product_id: int, duration: str, price: float) -> ProductPrice:
        existing = await self.get_price(product_id, duration)
        if existing:
            existing.price = price
            await self.session.commit()
            await cache.invalidate_pattern("products:*")
            return existing
        
        price_obj = ProductPrice(
            product_id=product_id,
            duration=duration,
            price=price
        )
        self.session.add(price_obj)
        await self.session.commit()
        await self.session.refresh(price_obj)
        await cache.invalidate_pattern("products:*")
        logger.info(f"💰 Price added: {product_id} - {duration}: {price}")
        return price_obj
    
    async def get_price(self, product_id: int, duration: str) -> Optional[ProductPrice]:
        stmt = select(ProductPrice).where(
            ProductPrice.product_id == product_id,
            ProductPrice.duration == duration
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def remove_price(self, price_id: int) -> bool:
        stmt = delete(ProductPrice).where(ProductPrice.id == price_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        await cache.invalidate_pattern("products:*")
        return result.rowcount > 0
    
    async def add_key(self, product_id: int, key_value: str, duration: str) -> ProductKey:
        key = ProductKey(
            product_id=product_id,
            key_value=key_value,
            duration=duration
        )
        self.session.add(key)
        await self.session.commit()
        await self.session.refresh(key)
        logger.info(f"🔑 Key added for product {product_id}")
        return key
    
    async def get_available_key(self, product_id: int, duration: str) -> Optional[ProductKey]:
        stmt = select(ProductKey).where(
            ProductKey.product_id == product_id,
            ProductKey.duration == duration,
            ProductKey.is_used == False
        ).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def mark_key_used(self, key_id: int) -> bool:
        stmt = select(ProductKey).where(ProductKey.id == key_id)
        result = await self.session.execute(stmt)
        key = result.scalar_one_or_none()
        
        if key:
            key.is_used = True
            await self.session.commit()
            return True
        return False
    
    async def get_keys_count(self, product_id: Optional[int] = None) -> dict:
        stmt = select(ProductKey)
        if product_id:
            stmt = stmt.where(ProductKey.product_id == product_id)
        
        result = await self.session.execute(stmt)
        keys = list(result.scalars().all())
        
        total = len(keys)
        available = len([k for k in keys if not k.is_used])
        used = total - available
        
        return {"total": total, "available": available, "used": used}
    
    async def remove_key(self, key_id: int) -> bool:
        stmt = delete(ProductKey).where(ProductKey.id == key_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_keys_for_product(self, product_id: int, unused_only: bool = False) -> List[ProductKey]:
        stmt = select(ProductKey).where(ProductKey.product_id == product_id)
        if unused_only:
            stmt = stmt.where(ProductKey.is_used == False)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def delete_all_keys(self, product_id: int) -> int:
        stmt = delete(ProductKey).where(ProductKey.product_id == product_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        logger.info(f"🗑️ Deleted all keys for product {product_id}: {result.rowcount} keys")
        return result.rowcount
    
    async def delete_claimed_keys(self, product_id: int) -> int:
        stmt = delete(ProductKey).where(
            ProductKey.product_id == product_id,
            ProductKey.is_used == True
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        logger.info(f"🗑️ Deleted claimed keys for product {product_id}: {result.rowcount} keys")
        return result.rowcount
    
    async def delete_last_generated_keys(self, product_id: int) -> int:
        stmt = select(ProductKey).where(ProductKey.product_id == product_id).order_by(ProductKey.created_at.desc())
        result = await self.session.execute(stmt)
        keys = list(result.scalars().all())
        
        if not keys:
            return 0
        
        last_batch_time = keys[0].created_at
        batch_keys = [k for k in keys if k.created_at == last_batch_time]
        
        if batch_keys:
            key_ids = [k.id for k in batch_keys]
            delete_stmt = delete(ProductKey).where(ProductKey.id.in_(key_ids))
            result = await self.session.execute(delete_stmt)
            await self.session.commit()
            logger.info(f"🗑️ Deleted last generated keys for product {product_id}: {result.rowcount} keys")
            return result.rowcount
        return 0
    
    async def get_product_stock(self, product_id: int) -> int:
        keys_data = await self.get_keys_count(product_id)
        return keys_data.get("available", 0)
    
    async def get_stock_per_duration(self, product_id: int) -> dict:
        """Get available stock count for each duration of a product"""
        stmt = select(ProductKey).where(
            ProductKey.product_id == product_id,
            ProductKey.is_used == False
        )
        result = await self.session.execute(stmt)
        keys = list(result.scalars().all())
        
        stock_by_duration = {}
        for key in keys:
            duration = key.duration
            normalized_duration = self._normalize_duration(duration)
            if normalized_duration not in stock_by_duration:
                stock_by_duration[normalized_duration] = 0
            stock_by_duration[normalized_duration] += 1
        
        return stock_by_duration
    
    def _normalize_duration(self, duration: str) -> str:
        """Normalize duration string to readable format for consistent matching"""
        import re
        if '|' in duration:
            return duration.split('|')[1]
        
        match = re.match(r'^(\d+)(d|m)$', duration.lower().strip())
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            if unit == 'd':
                return f"{num} Day{'s' if num > 1 else ''}"
            else:
                return f"{num} Month{'s' if num > 1 else ''}"
        
        return duration
