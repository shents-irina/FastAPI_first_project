from database import async_session_maker_null_pool
from schemas.hotels import HotelAdd
from utils.db_manager import DBManager


async def test_add_hotel(db):
    hotel_data = HotelAdd(title="Отель 5 звезд", location="г. Сочи, ул. Морская, 1")
    await db.hotels.add(hotel_data)
    await db.commit()
