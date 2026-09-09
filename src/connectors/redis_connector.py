import logging

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class RedisManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._redis: redis.Redis | None = None

    async def connect(self):
        logger.info("Начинаю подключение к Redis host=%s, port=%s", self.host, self.port)
        self._redis = redis.Redis(host=self.host, port=self.port)
        logger.info("Успешное подключение к Redis host=%s, port=%s", self.host, self.port)

    @property
    def redis(self) -> redis.Redis:
        if not self._redis:
            raise RuntimeError("Redis-соединение не установлено, вызовите connect()")
        return self._redis

    async def set(self, key: str, value: str, expire: int | None = None):
        await self.redis.set(key, value, ex=expire)

    async def get(self, key: str):
        return await self.redis.get(key)

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def close(self):
        if self._redis:
            await self._redis.aclose()
