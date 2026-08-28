from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models.bookings import BookingsORM
from models.rooms import RoomsORM
from repositories.base import BaseRepository
from repositories.mappers.mappers import BookingDataMapper
from repositories.utils import rooms_ids_for_booking
from schemas.bookings import BookingAdd


class BookingsRepository(BaseRepository):
    model = BookingsORM
    mapper = BookingDataMapper

    async def get_bookings_with_today_checkin(self):
        query = (
            select(BookingsORM)
            .options(
                joinedload(BookingsORM.user),
                joinedload(BookingsORM.room).joinedload(RoomsORM.hotel),
            )
            .filter(BookingsORM.date_from == datetime.now(tz=timezone.utc).date())
        )
        res = await self.session.execute(query)
        return res.scalars().unique().all()

    async def add_booking(self, data: BookingAdd, hotel_id: int | None = None):
        rooms_ids_to_get = rooms_ids_for_booking(
            date_from=data.date_from,
            date_to=data.date_to,
            hotel_id=hotel_id
        )
        rooms_ids_to_book: list[int] = (await self.session.execute(rooms_ids_to_get)).scalars().all()

        if data.room_id in rooms_ids_to_book:
            new_booking = await self.add(data)
            return new_booking
        else:
            raise HTTPException(status_code=409, detail="Нет свободных номеров на выбранные даты")
