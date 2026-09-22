from datetime import date

import sqlalchemy.exc
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from exceptions import ObjectNotFoundException
from models.rooms import RoomsORM
from repositories.base import BaseRepository
from repositories.mappers.mappers import RoomDataMapper, RoomWithRelsDataMapper
from repositories.utils import rooms_ids_for_booking
from schemas.rooms import Room


class RoomsRepository(BaseRepository[RoomsORM, Room]):
    model = RoomsORM
    mapper = RoomDataMapper

    async def get_filtered_by_time(
        self,
        hotel_id,
        date_from: date,
        date_to: date,
    ):
        rooms_ids_to_get = rooms_ids_for_booking(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )

        query = (
            select(self.model)
            .options(selectinload(self.model.facilities))
            .filter(RoomsORM.id.in_(rooms_ids_to_get))
        )
        result = await self.session.execute(query)
        return [
            RoomWithRelsDataMapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]

    async def get_one_with_rels(self, **filter_by):
        query = (
            select(self.model).options(selectinload(self.model.facilities)).filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except sqlalchemy.exc.NoResultFound as exc:
            raise ObjectNotFoundException from exc
        return RoomWithRelsDataMapper.map_to_domain_entity(model)
