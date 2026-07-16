from datetime import date

from models.rooms import RoomsORM
from repositories.base import BaseRepository
from repositories.utils import rooms_ids_for_booking
from schemas.rooms import Room


class RoomsRepository(BaseRepository):
    model = RoomsORM
    schema = Room

    async def get_filtered_by_time(
        self,
        hotel_id,
        date_from: date,
        date_to: date,
    ):
        rooms_ids_to_get = rooms_ids_for_booking(hotel_id=hotel_id, date_from=date_from, date_to=date_to)

        return await self.get_filtered(RoomsORM.id.in_(rooms_ids_to_get))
