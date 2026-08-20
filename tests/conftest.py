import json
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from config import settings
from database import Base, engine_null_pool, async_session_maker_null_pool
from main import app
from models import *
from schemas.hotels import HotelAdd
from schemas.rooms import RoomAdd
from utils.db_manager import DBManager


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[DBManager, None]:
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    with open("tests/mock_hotels.json", "r", encoding="utf-8") as json_hotels:
        hotels_data = json.load(json_hotels)
    with open("tests/mock_rooms.json", "r", encoding="utf-8") as json_rooms:
        rooms_data = json.load(json_rooms)

    async with DBManager(session_factory=async_session_maker_null_pool) as db_:
        await db_.hotels.add_bulk([HotelAdd.model_validate(h) for h in hotels_data])
        await db_.rooms.add_bulk([RoomAdd.model_validate(r) for r in rooms_data])
        await db_.commit()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def register_user(setup_database, ac):
    await ac.post(
        url="/auth/register",
        json={
            "email": "kot@pes.com",
            "password": "1234"
        }
    )
