from schemas.facilities import FacilityAdd
from schemas.hotels import HotelAdd
from schemas.rooms import RoomAdd


async def test_add_facility(db):
    facility = await db.facilities.add(FacilityAdd(title="Завтрак"))
    await db.commit()

    res = await db.facilities.get_one_or_none(id=facility.id)
    assert res is not None
    assert res.title == "Завтрак"


async def test_set_room_facilities_adds_and_replaces(db):
    hotel = await db.hotels.add(HotelAdd(title="Отель для m2m", location="г. Тест, ул. M2M, 1"))
    room = await db.rooms.add(
        RoomAdd(hotel_id=hotel.id, title="Номер для m2m", price=1000, quantity=1)
    )
    facility1 = await db.facilities.add(FacilityAdd(title="Удобство 1 для m2m"))
    facility2 = await db.facilities.add(FacilityAdd(title="Удобство 2 для m2m"))
    await db.commit()

    # привязываем только facility1.
    await db.rooms_facilities.set_room_facilities(room_id=room.id, facilities_ids={facility1.id})
    await db.commit()
    room_with_rels = await db.rooms.get_one_with_rels(id=room.id)
    assert {facility.id for facility in room_with_rels.facilities} == {facility1.id}

    # заменяем facility1 на facility2
    await db.rooms_facilities.set_room_facilities(room_id=room.id, facilities_ids={facility2.id})
    await db.commit()
    room_with_rels = await db.rooms.get_one_with_rels(id=room.id)
    assert {facility.id for facility in room_with_rels.facilities} == {facility2.id}

    # пустой набор
    await db.rooms_facilities.set_room_facilities(room_id=room.id, facilities_ids=set())
    await db.commit()
    room_with_rels = await db.rooms.get_one_with_rels(id=room.id)
    assert room_with_rels.facilities == []
