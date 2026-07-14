from datetime import date

from pydantic import BaseModel
from sqlalchemy import insert, select, func

from database import engine
from models.bookings import BookingsORM
from models.rooms import RoomsORM
from repositories.base import BaseRepository
from schemas.rooms import Room, RoomAdd


class RoomsRepository(BaseRepository):
    model = RoomsORM
    schema = Room

    async def get_filtered_by_time(
        self,
        hotel_id,
        date_from: date,
        date_to: date,
    ):
        """
        # Пример сырого запроса

        with rooms_count as (
            select room_id, count(*) as count_rooms_booked from bookings
            where date_from <= '2026-08-12' and date_to >= '2026-07-07'
            group by room_id
        ),
        rooms_left_table as (
            select rooms.id as room_id,  quantity - coalesce(count_rooms_booked, 0) as rooms_left
            from rooms
            left join rooms_count on rooms.id = rooms_count.room_id
        )
        select * from rooms_left_table
        where rooms_left > 0 and room_id in (select id from rooms where hotel_id = 3);
        """

        rooms_count = (
            select(BookingsORM.room_id, func.count().label("count_rooms_booked"))
            .select_from(BookingsORM)
            .filter(
                BookingsORM.date_from <= date_to,
                BookingsORM.date_to >= date_from
            )
            .group_by(BookingsORM.room_id)
            .cte(name="rooms_count")
        )

        rooms_left_table = (
            select(
                RoomsORM.id.label("room_id"),
                (RoomsORM.quantity - func.coalesce(rooms_count.c.count_rooms_booked, 0)).label("rooms_left")
            )
            .select_from(RoomsORM)
            .outerjoin(rooms_count, RoomsORM.id == rooms_count.c.room_id)
            .cte(name="rooms_left_table")
        )

        rooms_ids_for_hotel = (
            select(RoomsORM.id)
            .select_from(RoomsORM)
            .filter_by(hotel_id=hotel_id)
        )

        rooms_ids_to_get = (
            select(rooms_left_table.c.room_id)
            .select_from(rooms_left_table)
            .filter(
                rooms_left_table.c.rooms_left > 0,
                rooms_left_table.c.room_id.in_(rooms_ids_for_hotel),
            )
        )

        # print(rooms_ids_to_get.compile(bind=engine,compile_kwargs={"literal_binds": True }))

        return await self.get_filtered(RoomsORM.id.in_(rooms_ids_to_get))
