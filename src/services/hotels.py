import logging
from datetime import date

from exceptions import (
    HotelAlreadyExistsException,
    HotelNotFoundException,
    ObjectAlreadyExistsException,
    ObjectNotFoundException,
    check_date_to_after_date_from,
)
from schemas.hotels import Hotel, HotelAdd, HotelPatch
from schemas.pagination import PaginationParams
from services.base import BaseService

logger = logging.getLogger(__name__)


class HotelService(BaseService):
    """Сервис отелей: поиск, создание, изменение и удаление."""

    async def get_hotel_with_check(self, hotel_id: int) -> Hotel:
        """Возвращает отель по идентификатору.

        :raises HotelNotFoundException: Отеля с таким id нет.
        """
        try:
            return await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException as exc:
            raise HotelNotFoundException from exc

    async def get_hotels_filtered_by_time(
        self,
        pagination: PaginationParams,
        date_from: date,
        date_to: date,
        title: str | None,
        location: str | None,
    ):
        """Возвращает список отелей, доступных на выбранные даты, на запрошенной странице.

        Опционально фильтрует по названию и расположению.

        :param pagination: Номер страницы (начиная с 1) и размер страницы (по умолчанию 5 отелей).
        :param date_from: Начало периода.
        :param date_to: Конец периода.
        :param title: Фильтр по части названия, без учёта регистра.
        :param location: Фильтр по части адреса, без учёта регистра.
        :raises CheckOutBeforeCheckInException: Если дата выезда раньше даты заезда или совпадает с ней.
        """
        check_date_to_after_date_from(date_from, date_to)
        per_page = pagination.per_page or 5
        hotels = await self.db.hotels.get_filtered_by_time(
            date_from=date_from,
            date_to=date_to,
            title=title,
            location=location,
            offset=(pagination.page - 1) * per_page,
            limit=per_page,
        )
        return hotels

    async def add_hotel(self, hotel_data: HotelAdd):
        """Создаёт отель.

        :return: Созданный отель с присвоенным id.
        :raises HotelAlreadyExistsException: Такой отель уже существует.
        """
        try:
            hotel = await self.db.hotels.add(hotel_data)
        except ObjectAlreadyExistsException as exc:
            raise HotelAlreadyExistsException from exc
        await self.db.commit()
        logger.info("Создан отель hotel_id=%s", hotel.id)
        return hotel

    async def edit_hotel(self, hotel_id: int, hotel_data: HotelAdd):
        """Полностью заменяет данные отеля.

        :raises HotelNotFoundException: Отеля с таким id нет.
        :raises HotelAlreadyExistsException: Новые данные совпадают с другим существующим отелем.
        """
        await self.get_hotel_with_check(hotel_id)
        try:
            await self.db.hotels.edit(hotel_data, id=hotel_id)
        except ObjectAlreadyExistsException as exc:
            raise HotelAlreadyExistsException from exc
        await self.db.commit()
        logger.info("Отель изменён hotel_id=%s", hotel_id)

    async def edit_hotel_partially(self, hotel_id: int, hotel_data: HotelPatch):
        """Изменяет только переданные поля отеля.

        Поля, которые не были заданы в ``hotel_data``, остаются прежними.

        :raises HotelNotFoundException: Отеля с таким id нет.
        :raises HotelAlreadyExistsException: Новые данные совпадают с другим существующим отелем.
        """
        await self.get_hotel_with_check(hotel_id)
        try:
            await self.db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
        except ObjectAlreadyExistsException as exc:
            raise HotelAlreadyExistsException from exc
        await self.db.commit()
        logger.info("Отель частично изменён hotel_id=%s", hotel_id)

    async def delete_hotel(self, hotel_id: int):
        """Удаляет отель.

        Номера отеля удаляются вместе с ним каскадно, но только если ни на один из них нет бронирований.

        :raises HotelNotFoundException: Отеля с таким id нет.
        :raises ObjectIsInUseException: У номеров отеля есть бронирования.
        """
        await self.get_hotel_with_check(hotel_id)
        await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()
        logger.info("Отель удалён hotel_id=%s", hotel_id)
