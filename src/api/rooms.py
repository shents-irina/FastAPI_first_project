from datetime import date

from fastapi import APIRouter, Body, Query
from fastapi_cache.decorator import cache

from api.dependencies import DBDep
from exceptions import (
    CheckOutBeforeCheckInException,
    CheckOutBeforeCheckInHTTPException,
    FacilityNotFoundException,
    FacilityNotFoundHTTPException,
    HotelNotFoundException,
    HotelNotFoundHTTPException,
    ObjectIsInUseException,
    ObjectIsInUseHTTPException,
    RoomAlreadyExistsException,
    RoomAlreadyExistsHTTPException,
    RoomNotFoundException,
    RoomNotFoundHTTPException,
)
from schemas.rooms import RoomAddRequest, RoomPatchRequest
from services.rooms import RoomService

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get(
    path="/{hotel_id}/rooms",
    summary="Получение доступных номеров отеля",
)
async def get_rooms(
    db: DBDep,
    hotel_id: int,
    date_from: date = Query(
        openapi_examples={"example1": {"summary": "Пример даты заезда", "value": "2026-07-07"}}
    ),
    date_to: date = Query(
        openapi_examples={"example1": {"summary": "Пример даты выезда", "value": "2026-08-12"}}
    ),
):
    try:
        return await RoomService(db).get_rooms_filtered_by_time(hotel_id, date_from, date_to)
    except HotelNotFoundException as exc:
        raise HotelNotFoundHTTPException from exc
    except CheckOutBeforeCheckInException as exc:
        raise CheckOutBeforeCheckInHTTPException from exc


@router.get(path="/{hotel_id}/rooms/{room_id}", summary="Получение конкретного номера отеля")
@cache(expire=60)
async def get_room(db: DBDep, hotel_id: int, room_id: int):
    try:
        return await RoomService(db).get_room(hotel_id, room_id)
    except HotelNotFoundException as exc:
        raise HotelNotFoundHTTPException from exc
    except RoomNotFoundException as exc:
        raise RoomNotFoundHTTPException from exc


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
            "1": {
                "summary": "Пример данных номера",
                "value": {
                    "title": "Комфорт",
                    "description": "Номер с видом на море",
                    "price": 5000,
                    "quantity": 5,
                    "facilities_ids": [2, 3],
                },
            }
        }
    ),
):
    try:
        room = await RoomService(db).create_room(hotel_id, room_data)
    except HotelNotFoundException as exc:
        raise HotelNotFoundHTTPException from exc
    except RoomAlreadyExistsException as exc:
        raise RoomAlreadyExistsHTTPException from exc
    except FacilityNotFoundException as exc:
        raise FacilityNotFoundHTTPException from exc

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
    try:
        await RoomService(db).edit_room(hotel_id, room_id, room_data)
    except HotelNotFoundException as exc:
        raise HotelNotFoundHTTPException from exc
    except RoomNotFoundException as exc:
        raise RoomNotFoundHTTPException from exc
    except RoomAlreadyExistsException as exc:
        raise RoomAlreadyExistsHTTPException from exc
    except FacilityNotFoundException as exc:
        raise FacilityNotFoundHTTPException from exc

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
    try:
        await RoomService(db).partial_edit_room(hotel_id, room_id, room_data)
    except HotelNotFoundException as exc:
        raise HotelNotFoundHTTPException from exc
    except RoomNotFoundException as exc:
        raise RoomNotFoundHTTPException from exc
    except RoomAlreadyExistsException as exc:
        raise RoomAlreadyExistsHTTPException from exc
    except FacilityNotFoundException as exc:
        raise FacilityNotFoundHTTPException from exc

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
    try:
        await RoomService(db).delete_room(hotel_id, room_id)
    except HotelNotFoundException as exc:
        raise HotelNotFoundHTTPException from exc
    except RoomNotFoundException as exc:
        raise RoomNotFoundHTTPException from exc
    except ObjectIsInUseException as exc:
        raise ObjectIsInUseHTTPException from exc

    return {"status": "OK"}
