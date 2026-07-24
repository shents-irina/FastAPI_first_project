from datetime import date

from fastapi import APIRouter, Body, Query

from api.dependencies import DBDep
from schemas.facilities import RoomFacilityAdd
from schemas.rooms import RoomAdd, RoomAddRequest, RoomPatch, RoomPatchRequest


router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get(
    path="/{hotel_id}/rooms",
    summary="Получение номеров отеля",
)
async def get_rooms(
    db: DBDep,
    hotel_id: int,
    date_from: date = Query(examples=["2026-07-10"]),
    date_to: date = Query(examples=["2026-07-20"]),
):
    return await db.rooms.get_filtered_by_time(hotel_id=hotel_id, date_from=date_from, date_to=date_to)


@router.get(
    path="/{hotel_id}/rooms/{room_id}",
    summary="Получение конкретного номера отеля"
)
async def get_room(
    db: DBDep,
    hotel_id: int,
    room_id: int
):
    return await db.rooms.get_one_or_none_with_rels(hotel_id=hotel_id, id=room_id)


@router.post(
    path="/{hotel_id}/rooms",
    summary="Регистрация номера",
    description="Добавление данных номера для отеля",
)
async def create_room(
    db: DBDep,
    hotel_id: int,
    room_data: RoomAddRequest = Body(
        openapi_examples={
            "1": {"summary": "Пример данных номера", "value": {
                "title": "Комфорт",
                "description": "Номер с видом на море",
                "price": 5000,
                "quantity": 5,
                "facilities_ids": [2, 3]
            }}
        }
    )
):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    room = await db.rooms.add(_room_data)

    rooms_facilities_data = [RoomFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in room_data.facilities_ids]
    await db.rooms_facilities.add_bulk(rooms_facilities_data)
    await db.commit()

    return {"status": "OK", "data": room}


@router.put(
    path="/{hotel_id}/rooms/{room_id}",
    summary="Замена данных номера",
    description="Полная замена данных номера отеля",
)
async def edit_room(
    db: DBDep,
    hotel_id: int,
    room_id: int,
    room_data: RoomAddRequest,
):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    await db.rooms.edit(_room_data, id=room_id, hotel_id=hotel_id )
    await db.rooms_facilities.set_room_facilities(room_id=room_id, facilities_ids=room_data.facilities_ids)
    await db.commit()
    return {"status": "OK"}


@router.patch(
    path="/{hotel_id}/rooms/{room_id}",
    summary="Частичная замена данных номера",
    description="Заменяем какие-то конкретные данные номера отеля",
)
async def partial_edit_room(
    db: DBDep,
    hotel_id: int,
    room_id: int,
    room_data: RoomPatchRequest,
):
    _room_data_dict = room_data.model_dump(exclude_unset=True)
    _room_data = RoomPatch(hotel_id=hotel_id, **_room_data_dict)
    await db.rooms.edit(_room_data, exclude_unset=True, id=room_id, hotel_id=hotel_id)
    if "facilities_ids" in _room_data_dict:
        await db.rooms_facilities.set_room_facilities(room_id=room_id, facilities_ids=_room_data_dict["facilities_ids"])
    await db.commit()
    return {"status": "OK"}


@router.delete(
    path="/{hotel_id}/rooms/{room_id}",
    summary="Удаление данных номера отеля",
)
async def delete_room(
    db: DBDep,
    hotel_id: int,
    room_id: int,
):
    await db.rooms.delete(hotel_id=hotel_id, id=room_id)
    await db.commit()
    return {"status": "OK"}
