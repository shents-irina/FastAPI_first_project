import logging
from datetime import date

from exceptions import (
    FacilityNotFoundException,
    ObjectAlreadyExistsException,
    ObjectNotFoundException,
    RoomAlreadyExistsException,
    RoomNotFoundException,
    check_date_to_after_date_from,
)
from schemas.facilities import RoomFacilityAdd
from schemas.rooms import Room, RoomAdd, RoomAddRequest, RoomPatch, RoomPatchRequest
from services.base import BaseService
from services.hotels import HotelService

logger = logging.getLogger(__name__)


class RoomService(BaseService):
    """Сервис номеров: поиск, создание, изменение и удаление.

    Почти все методы сначала проверяют, что отель существует, и только потом работают с номером,
    поэтому снаружи можно получить как ``HotelNotFoundException``, так и ``RoomNotFoundException``.
    """

    async def get_room_with_check(self, room_id: int) -> Room:
        """Возвращает номер по идентификатору.

        :raises RoomNotFoundException: Номера с таким id нет.
        """
        try:
            return await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException as exc:
            raise RoomNotFoundException from exc

    async def get_rooms_filtered_by_time(self, hotel_id: int, date_from: date, date_to: date):
        """Возвращает список номеров отеля, свободные на выбранные даты (вместе с удобствами).

        :raises HotelNotFoundException: Отеля с таким id нет.
        :raises CheckOutBeforeCheckInException Если date_to раньше date_from или совпадает с ней.
        """
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        check_date_to_after_date_from(date_from, date_to)
        return await self.db.rooms.get_filtered_by_time(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )

    async def get_room(self, hotel_id: int, room_id: int):
        """Возвращает номер отеля вместе со связанными удобствами.

        :raises HotelNotFoundException: Отеля с таким id нет.
        :raises RoomNotFoundException: В этом отеле нет номера с таким id.
        """
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        try:
            return await self.db.rooms.get_one_with_rels(id=room_id, hotel_id=hotel_id)
        except ObjectNotFoundException as exc:
            raise RoomNotFoundException from exc

    async def create_room(self, hotel_id: int, room_data: RoomAddRequest):
        """Создаёт номер в отеле и привязывает к нему удобства.

        Номер и связи с удобствами создаются в одной транзакции.

        :return: Созданный номер.
        :raises HotelNotFoundException: Отеля с таким id нет.
        :raises RoomAlreadyExistsException: В отеле уже есть номер с таким названием.
        :raises FacilityNotFoundException: Среди ``facilities_ids`` есть несуществующее удобство.
        """
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        try:
            room = await self.db.rooms.add(_room_data)
        except ObjectAlreadyExistsException as exc:
            raise RoomAlreadyExistsException from exc

        rooms_facilities_data = [
            RoomFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in room_data.facilities_ids
        ]
        try:
            await self.db.rooms_facilities.add_bulk(rooms_facilities_data)
        except ObjectNotFoundException as exc:
            raise FacilityNotFoundException from exc
        await self.db.commit()

        logger.info("Создан номер room_id=%s в отеле hotel_id=%s", room.id, hotel_id)
        return room

    async def edit_room(self, hotel_id: int, room_id: int, room_data: RoomAddRequest):
        """Полностью заменяет данные номера и набор его удобств.

        :raises HotelNotFoundException: Отеля с таким id нет.
        :raises RoomNotFoundException: Номера с таким id нет.
        :raises RoomAlreadyExistsException: В отеле уже есть другой номер с таким названием.
        :raises FacilityNotFoundException: Среди ``facilities_ids`` есть несуществующее удобство.
        """
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)

        _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        try:
            await self.db.rooms.edit(_room_data, id=room_id, hotel_id=hotel_id)
        except ObjectAlreadyExistsException as exc:
            raise RoomAlreadyExistsException from exc
        try:
            await self.db.rooms_facilities.set_room_facilities(
                room_id=room_id, facilities_ids=room_data.facilities_ids
            )
        except ObjectNotFoundException as exc:
            raise FacilityNotFoundException from exc
        await self.db.commit()
        logger.info("Номер изменён room_id=%s, hotel_id=%s", room_id, hotel_id)

    async def partial_edit_room(self, hotel_id: int, room_id: int, room_data: RoomPatchRequest):
        """Изменяет только переданные поля номера.

        Набор удобств обновляется, только если ``facilities_ids`` явно передан в запросе.

        :raises HotelNotFoundException: Отеля с таким id нет.
        :raises RoomNotFoundException: Номера с таким id нет.
        :raises RoomAlreadyExistsException: В отеле уже есть другой номер с таким названием.
        :raises FacilityNotFoundException: Среди ``facilities_ids`` есть несуществующее удобство.
        """
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)

        _room_data_dict = room_data.model_dump(exclude_unset=True)
        _room_data = RoomPatch(hotel_id=hotel_id, **_room_data_dict)
        try:
            await self.db.rooms.edit(_room_data, exclude_unset=True, id=room_id, hotel_id=hotel_id)
        except ObjectAlreadyExistsException as exc:
            raise RoomAlreadyExistsException from exc

        if "facilities_ids" in _room_data_dict:
            try:
                await self.db.rooms_facilities.set_room_facilities(
                    room_id=room_id, facilities_ids=_room_data_dict["facilities_ids"]
                )
            except ObjectNotFoundException as exc:
                raise FacilityNotFoundException from exc
        await self.db.commit()
        logger.info("Номер частично изменён room_id=%s, hotel_id=%s", room_id, hotel_id)

    async def delete_room(self, hotel_id: int, room_id: int):
        """Удаляет номер отеля.

        :raises HotelNotFoundException: Отеля с таким id нет.
        :raises RoomNotFoundException: Номера с таким id нет.
        :raises ObjectIsInUseException: У номера есть бронирование.
        """
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)

        await self.db.rooms.delete(hotel_id=hotel_id, id=room_id)
        await self.db.commit()
        logger.info("Номер удалён room_id=%s, hotel_id=%s", room_id, hotel_id)
