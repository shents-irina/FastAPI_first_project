from fastapi import APIRouter, Body

from api.dependencies import DBDep
from schemas.rooms import RoomAdd, RoomAddRequest, RoomPatch, RoomPatchRequest


router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get(
    path="/{hotel_id}/rooms",
    summary="Получение номеров отеля",
)
async def get_rooms(
    db: DBDep,
    hotel_id: int
):
    return await db.rooms.get_filtered(hotel_id=hotel_id)


@router.get(
    path="/{hotel_id}/rooms/{room_id}",
    summary="Получение конкретного номера отеля"
)
async def get_room(
    db: DBDep,
    hotel_id: int,
    room_id: int
):
    return await db.rooms.get_one_or_none(hotel_id=hotel_id, id=room_id)


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
                "quantity": 5
            }}
        }
    )
):
    _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
    room = await db.rooms.add(_room_data)
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
    _room_data = RoomPatch(hotel_id=hotel_id, **room_data.model_dump(exclude_unset=True))
    await db.rooms.edit(_room_data, exclude_unset=True, id=room_id, hotel_id=hotel_id)
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
