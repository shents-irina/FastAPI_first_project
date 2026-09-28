from exceptions import (
    BookingNotFoundException,
    ObjectNotFoundException,
    check_booking_not_in_past,
    check_booking_not_started,
    check_date_to_after_date_from,
)
from schemas.bookings import Booking, BookingAdd, BookingAddRequest
from services.base import BaseService
from services.rooms import RoomService


class BookingService(BaseService):
    async def get_booking_with_check(self, booking_id: int, user_id: int) -> Booking:
        try:
            return await self.db.bookings.get_one(id=booking_id, user_id=user_id)
        except ObjectNotFoundException as exc:
            raise BookingNotFoundException from exc

    async def get_bookings(self):
        return await self.db.bookings.get_all()

    async def get_my_bookings(self, user_id: int):
        return await self.db.bookings.get_filtered(user_id=user_id)

    async def add_booking(self, user_id: int, booking_data: BookingAddRequest):
        room = await RoomService(self.db).get_room_with_check(room_id=booking_data.room_id)
        check_date_to_after_date_from(booking_data.date_from, booking_data.date_to)
        check_booking_not_in_past(booking_data.date_from)

        room_price: int = room.price
        hotel_id: int = room.hotel_id
        _booking_data = BookingAdd(**booking_data.model_dump(), user_id=user_id, price=room_price)
        booking = await self.db.bookings.add_booking(_booking_data, hotel_id=hotel_id)
        await self.db.commit()

        return booking

    async def delete_booking(self, user_id: int, booking_id: int):
        booking = await self.get_booking_with_check(booking_id, user_id)
        check_booking_not_started(date_from=booking.date_from)

        await self.db.bookings.delete(id=booking_id, user_id=user_id)
        await self.db.commit()
