import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import redis.exceptions as redis_exceptions
import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend

sys.path.append(str(Path(__file__).parent.parent))

from config import settings

logging.basicConfig(
    level=logging.DEBUG if settings.MODE != "PROD" else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

from api.auth import router as router_auth
from api.bookings import router as router_bookings
from api.facilities import router as router_facilities
from api.hotels import router as router_hotels
from api.images import router as router_images
from api.rooms import router as router_rooms
from init import redis_manager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управляет жизненным циклом приложения.

    При запуске проверяет доступность Redis и использует его для кэширования ответов.
    Если проверка завершается ошибкой ``RedisError``, использует ``InMemoryBackend``.
    Выбор хранилища выполняется только при запуске приложения.
    При остановке приложения подключение к Redis закрывается (если оно было открыто).
    """
    logger.info("Приложение запускается, MODE=%s", settings.MODE)
    try:
        await redis_manager.connect()
        FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
        logger.info("Для кэширования используется Redis")
    except redis_exceptions.RedisError:
        FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
        logger.info("Для кэширования используется InMemoryBackend, т.к. Redis недоступен")
    logger.info("Кэш FastAPI инициализирован")
    yield
    logger.info("Приложение останавливается")
    await redis_manager.close()


app = FastAPI(lifespan=lifespan)

app.include_router(router_auth)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_facilities)
app.include_router(router_bookings)
app.include_router(router_images)

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
