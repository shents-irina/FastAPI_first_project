import pytest

from exceptions import ObjectAlreadyExistsException
from schemas.hotels import HotelAdd


async def test_add_hotel(db):
    hotel_data = HotelAdd(title="Отель 5 звезд", location="г. Сочи, ул. Морская, 1")
    new_hotel = await db.hotels.add(hotel_data)
    await db.commit()

    assert new_hotel is not None
    assert new_hotel.title == hotel_data.title
    assert new_hotel.location == hotel_data.location


async def test_add_duplicate_hotel_raises_already_exists(db):
    hotel_data = HotelAdd(title="Уникальный отель", location="г. Уникальный, ул. Тестовая, 1")
    await db.hotels.add(hotel_data)
    await db.commit()

    with pytest.raises(ObjectAlreadyExistsException):
        await db.hotels.add(hotel_data)


async def test_get_one_or_none_returns_none_for_missing_hotel(db):
    hotel = await db.hotels.get_one_or_none(id=999999)
    assert hotel is None


async def test_delete_hotel(db):
    hotel = await db.hotels.add(
        HotelAdd(title="Отель для удаления", location="г. Удаление, ул. Первая, 1")
    )
    await db.commit()

    await db.hotels.delete(id=hotel.id)
    await db.commit()

    assert await db.hotels.get_one_or_none(id=hotel.id) is None
