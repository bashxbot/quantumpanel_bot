import json
from typing import Optional, Any
import redis.asyncio as redis
from loguru import logger

from bot.config import config


class CacheService:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self):
        try:
            self.redis = redis.from_url(
                config.redis.url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis.ping()
            self._connected = True
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Running without cache.")
            self._connected = False
    
    async def disconnect(self):
        if self.redis and self._connected:
            await self.redis.close()
            logger.info("🔌 Redis disconnected")
    
    async def get(self, key: str) -> Optional[Any]:
        if not self._connected:
            return None
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: int = 300):
        if not self._connected:
            return
        try:
            await self.redis.set(key, json.dumps(value), ex=expire)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    async def delete(self, key: str):
        if not self._connected:
            return
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
    
    async def invalidate_pattern(self, pattern: str):
        if not self._connected:
            return
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Redis invalidate error: {e}")


cache = CacheService()
