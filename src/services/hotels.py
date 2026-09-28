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


class HotelService(BaseService):
    async def get_hotel_with_check(self, hotel_id: int) -> Hotel:
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
        try:
            hotel = await self.db.hotels.add(hotel_data)
        except ObjectAlreadyExistsException as exc:
            raise HotelAlreadyExistsException from exc
        await self.db.commit()
        return hotel

    async def edit_hotel(self, hotel_id: int, hotel_data: HotelAdd):
        await self.get_hotel_with_check(hotel_id)
        try:
            await self.db.hotels.edit(hotel_data, id=hotel_id)
        except ObjectAlreadyExistsException as exc:
            raise HotelAlreadyExistsException from exc
        await self.db.commit()

    async def edit_hotel_partially(self, hotel_id: int, hotel_data: HotelPatch):
        await self.get_hotel_with_check(hotel_id)
        try:
            await self.db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
        except ObjectAlreadyExistsException as exc:
            raise HotelAlreadyExistsException from exc
        await self.db.commit()

    async def delete_hotel(self, hotel_id: int):
        await self.get_hotel_with_check(hotel_id)
        await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()
