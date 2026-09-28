from fastapi import APIRouter

from api.dependencies import DBDep, UserIdDep
from exceptions import (
    AllRoomsAreBookedException,
    AllRoomsAreBookedHTTPException,
    BookingAlreadyStartedException,
    BookingAlreadyStartedHTTPException,
    BookingDateInPastException,
    BookingDateInPastHTTPException,
    BookingNotFoundException,
    BookingNotFoundHTTPException,
    CheckOutBeforeCheckInException,
    CheckOutBeforeCheckInHTTPException,
    RoomNotFoundException,
    RoomNotFoundHTTPException,
)
from schemas.bookings import BookingAddRequest
from services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get(path="", summary="Получение всех бронирований")
async def get_bookings(
    db: DBDep,
):
    return await BookingService(db).get_bookings()


@router.get(path="/me", summary="Получение своих бронирований")
async def get_my_bookings(
    user_id: UserIdDep,
    db: DBDep,
):
    return await BookingService(db).get_my_bookings(user_id)


@router.post(path="", summary="Бронирование номера отеля")
async def add_booking(db: DBDep, user_id: UserIdDep, booking_data: BookingAddRequest):
    try:
        booking = await BookingService(db).add_booking(user_id, booking_data)
    except RoomNotFoundException as exc:
        raise RoomNotFoundHTTPException from exc
    except CheckOutBeforeCheckInException as exc:
        raise CheckOutBeforeCheckInHTTPException from exc
    except BookingDateInPastException as exc:
        raise BookingDateInPastHTTPException from exc
    except AllRoomsAreBookedException as exc:
        raise AllRoomsAreBookedHTTPException from exc
    return {"status": "OK", "data": booking}


@router.delete("/{booking_id}", summary="Удаление бронирования номера")
async def delete_booking(db: DBDep, user_id: UserIdDep, booking_id: int):
    try:
        await BookingService(db).delete_booking(user_id, booking_id)
    except BookingNotFoundException as exc:
        raise BookingNotFoundHTTPException from exc
    except BookingAlreadyStartedException as exc:
        raise BookingAlreadyStartedHTTPException from exc
    return {"status": "OK"}
