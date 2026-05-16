import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import text

from src.config import settings


engine = create_async_engine(url=settings.DB_URL)


