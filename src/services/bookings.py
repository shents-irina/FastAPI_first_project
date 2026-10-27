import logging

from exceptions import (
    AllRoomsAreBookedException,
    BookingNotFoundException,
    ObjectNotFoundException,
    check_booking_not_in_past,
    check_booking_not_started,
    check_date_to_after_date_from,
)
from schemas.bookings import Booking, BookingAdd, BookingAddRequest
from services.base import BaseService
from services.rooms import RoomService

logger = logging.getLogger(__name__)


class BookingService(BaseService):
    """Сервис бронирований: просмотр, создание и отмена."""

    async def get_booking_with_check(self, booking_id: int, user_id: int) -> Booking:
        """Возвращает бронирование, принадлежащее пользователю.

        Поиск идёт сразу по идентификатору брони и по владельцу, чужое бронирование считается ненайденным.

        :raises BookingNotFoundException: Бронирования с такими параметрами нет.
        """
        try:
            return await self.db.bookings.get_one(id=booking_id, user_id=user_id)
        except ObjectNotFoundException as exc:
            raise BookingNotFoundException from exc

    async def get_bookings(self):
        """Возвращает список всех бронирований всех пользователей."""
        return await self.db.bookings.get_all()

    async def get_my_bookings(self, user_id: int):
        """Возвращает бронирования одного пользователя.

        :return: Список бронирований пользователя.
        """
        return await self.db.bookings.get_filtered(user_id=user_id)

    async def add_booking(self, user_id: int, booking_data: BookingAddRequest):
        """Создаёт бронирование номера на период.

        Проверяет, что номер существует, период корректен.
        Цена фиксируется в момент бронирования: последующее изменение цены номера уже созданные брони не затрагивает.

        :param user_id: Идентификатор пользователя, который бронирует.
        :param booking_data: Номер и даты заезда и выезда.
        :return: Созданное бронирование.
        :raises AllRoomsAreBookedException: На указанный период нет свободных номеров.
        """
        room = await RoomService(self.db).get_room_with_check(room_id=booking_data.room_id)
        check_date_to_after_date_from(booking_data.date_from, booking_data.date_to)
        check_booking_not_in_past(booking_data.date_from)

        room_price: int = room.price
        hotel_id: int = room.hotel_id
        _booking_data = BookingAdd(**booking_data.model_dump(), user_id=user_id, price=room_price)
        try:
            booking = await self.db.bookings.add_booking(_booking_data, hotel_id=hotel_id)
        except AllRoomsAreBookedException:
            logger.info(
                "Нет свободных номеров: room_id=%s, user_id=%s, %s - %s",
                booking_data.room_id,
                user_id,
                booking_data.date_from,
                booking_data.date_to,
            )
            raise
        await self.db.commit()

        logger.info(
            "Создано бронирование booking_id=%s: user_id=%s, room_id=%s, %s - %s",
            booking.id,
            user_id,
            booking.room_id,
            booking.date_from,
            booking.date_to,
        )
        return booking

    async def delete_booking(self, user_id: int, booking_id: int):
        """Отменяет бронирование пользователя до начала заезда.

        :raises BookingNotFoundException: Бронирования с такими параметрами нет.
        :raises BookingAlreadyStartedException: Если дата заезда совпадает с текущей или находится в прошлом.
        """
        booking = await self.get_booking_with_check(booking_id, user_id)
        check_booking_not_started(date_from=booking.date_from)

        await self.db.bookings.delete(id=booking_id, user_id=user_id)
        await self.db.commit()
        logger.info("Бронирование отменено booking_id=%s, user_id=%s", booking_id, user_id)
