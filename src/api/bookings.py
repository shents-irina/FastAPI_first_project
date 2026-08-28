from fastapi import APIRouter

from api.dependencies import DBDep, UserIdDep
from schemas.bookings import BookingAdd, BookingAddRequest

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get(
    path="",
    summary="Получение всех бронирований"
)
async def get_bookings(
    db: DBDep,
):
    return await db.bookings.get_all()


@router.get(
    path="/me",
    summary="Получение своих бронирований"
)
async def get_my_bookings(
    user_id: UserIdDep,
    db: DBDep,
):
    return await db.bookings.get_filtered(user_id=user_id)


@router.post(
    path="",
    summary="Бронирование номера отеля"
)
async def add_booking(
    db: DBDep,
    user_id: UserIdDep,
    booking_data: BookingAddRequest
):
    room = await db.rooms.get_one_or_none(id=booking_data.room_id)
    room_price: int = room.price
    hotel_id: int = room.hotel_id
    _booking_data = BookingAdd(**booking_data.model_dump(), user_id=user_id, price=room_price)
    booking =  await db.bookings.add_booking(_booking_data, hotel_id=hotel_id)
    await db.commit()
    return {"status": "OK", "data": booking}
