import json
import os
from typing import Optional, Any
import aiohttp
from loguru import logger

from bot.config import config


class CacheService:
    def __init__(self):
        self._connected = False
        self._rest_url = None
        self._rest_token = None
    
    async def connect(self):
        self._rest_url = os.getenv("REDIS_REST_URL", "").strip()
        self._rest_token = os.getenv("REDIS_REST_TOKEN", "").strip()
        
        if not self._rest_url or not self._rest_token:
            logger.info("📦 No Redis REST credentials configured. Running without cache.")
            self._connected = False
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self._rest_token}"}
                async with session.get(f"{self._rest_url}/ping", headers=headers) as resp:
                    if resp.status == 200:
                        self._connected = True
                        logger.info("✅ Redis REST API connected successfully")
                    else:
                        logger.warning(f"⚠️ Redis REST ping failed with status {resp.status}")
                        self._connected = False
        except Exception as e:
            logger.warning(f"⚠️ Redis REST connection failed: {e}. Running without cache.")
            self._connected = False
    
    async def disconnect(self):
        if self._connected:
            self._connected = False
            logger.info("🔌 Redis disconnected")
    
    async def _request(self, command: list) -> Optional[Any]:
        if not self._connected:
            return None
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self._rest_token}"}
                async with session.post(
                    self._rest_url,
                    headers=headers,
                    json=command
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("result")
                    return None
        except Exception as e:
            logger.error(f"Redis REST error: {e}")
            return None
    
    async def get(self, key: str) -> Optional[Any]:
        if not self._connected:
            return None
        try:
            result = await self._request(["GET", key])
            if result:
                return json.loads(result)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: int = 300):
        if not self._connected:
            return
        try:
            json_value = json.dumps(value)
            await self._request(["SET", key, json_value, "EX", str(expire)])
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    async def delete(self, key: str):
        if not self._connected:
            return
        try:
            await self._request(["DEL", key])
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
    
    async def invalidate_pattern(self, pattern: str):
        if not self._connected:
            return
        try:
            cursor = "0"
            while True:
                result = await self._request(["SCAN", cursor, "MATCH", pattern, "COUNT", "100"])
                if not result or len(result) < 2:
                    break
                cursor, keys = result[0], result[1]
                if keys:
                    for key in keys:
                        await self._request(["DEL", key])
                if cursor == "0":
                    break
        except Exception as e:
            logger.error(f"Redis invalidate error: {e}")


cache = CacheService()
