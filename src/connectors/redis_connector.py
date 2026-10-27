import logging

import redis.asyncio as aredis
import redis.exceptions

logger = logging.getLogger(__name__)


class RedisManager:
    """Хранит асинхронный клиент Redis и предоставляет операции с ключами.

    Клиент инициализируется методом ``connect()`` при запуске приложения.
    Метод ``close()`` закрывает клиент и его соединение.
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._redis: aredis.Redis | None = None

    async def connect(self):
        """Создаёт клиент и проверяет, что Redis отвечает.

        Сохраняет клиент только после успешной проверки.
        При неудаче закрывает временный клиент и пробрасывает ошибку.

        :raises redis_exceptions.RedisError: Если не удалось подключиться к Redis.
        """
        logger.info("Начинаю подключение к Redis host=%s, port=%s", self.host, self.port)
        client = aredis.Redis(host=self.host, port=self.port)
        try:
            await client.ping()
        except redis.exceptions.RedisError:
            logger.warning("Не удалось подключиться к Redis host=%s, port=%s", self.host, self.port)
            raise
        self._redis = client
        logger.info("Успешное подключение к Redis host=%s, port=%s", self.host, self.port)

    @property
    def redis(self) -> aredis.Redis:
        """Возвращает инициализированный клиент Redis.

        :raises RuntimeError: Если клиент не инициализирован или уже закрыт.
        """
        if not self._redis:
            raise RuntimeError("Redis-соединение не установлено, вызовите connect()")
        return self._redis

    async def set(self, key: str, value: str, expire: int | None = None):
        """Записывает значение по ключу, заменяя существующее.

        :param key: Ключ Redis.
        :param value: Сохраняемая строка.
        :param expire:
            Срок хранения в секундах. Если ``None``, значение записывается без срока истечения.
        """
        await self.redis.set(key, value, ex=expire)

    async def get(self, key: str):
        """Возвращает значение по ключу.

        :param key: Ключ Redis.
        :return: Сохранённое значение или ``None``, если ключ отсутствует.
        """
        return await self.redis.get(key)

    async def delete(self, key: str):
        """Удаляет ключ и связанное с ним значение.

        Если ключ отсутствует, ничего не делает.

        :param key: Удаляемый ключ.
        """
        await self.redis.delete(key)

    async def close(self):
        """Закрывает соединение Redis."""
        if self._redis:
            await self._redis.aclose()
            self._redis = None
            logger.info("Соединение с Redis закрыто")
