import json
import os
import ssl
from typing import Optional, Any
import redis.asyncio as redis
from loguru import logger

from bot.config import config


class CacheService:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self):
        redis_url = config.redis.url
        
        if not redis_url or redis_url.strip() == "":
            logger.info("📦 No Redis URL configured. Running without cache.")
            self._connected = False
            return
        
        try:
            connection_kwargs = {
                "encoding": "utf-8",
                "decode_responses": True,
            }
            
            if redis_url.startswith("rediss://"):
                ssl_verify = os.getenv("REDIS_SSL_VERIFY", "false").lower() == "true"
                
                if ssl_verify:
                    ssl_context = ssl.create_default_context()
                else:
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                
                connection_kwargs["ssl"] = ssl_context
            
            self.redis = redis.from_url(redis_url, **connection_kwargs)
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
