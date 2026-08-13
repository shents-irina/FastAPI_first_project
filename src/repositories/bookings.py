from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models.bookings import BookingsORM
from models.rooms import RoomsORM
from repositories.base import BaseRepository
from repositories.mappers.mappers import BookingDataMapper


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
            .filter(BookingsORM.date_from == date.today())
        )
        res = await self.session.execute(query)
        return res.scalars().unique().all()
