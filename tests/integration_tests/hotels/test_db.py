from database import async_session_maker_null_pool
from schemas.hotels import HotelAdd
from utils.db_manager import DBManager


async def test_add_hotel():
    hotel_data = HotelAdd(title="Отель 5 звезд", location="г. Сочи, ул. Морская, 1")
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        await db.hotels.add(hotel_data)
        await db.commit()
