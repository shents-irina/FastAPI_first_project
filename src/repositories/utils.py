from datetime import date

from sqlalchemy import select, func

from database import engine
from models.bookings import BookingsORM
from models.rooms import RoomsORM


def rooms_ids_for_booking(
    date_from: date,
    date_to: date,
    hotel_id : int | None = None,
):
    """
    # Пример сырого запроса:
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
    select room_id from rooms_left_table
    where rooms_left > 0 and room_id in (select id from rooms where hotel_id = 3);
    """
    rooms_booked_data = (
        select(BookingsORM.room_id, func.count().label("count_rooms_booked"))
        .select_from(BookingsORM)
        .filter(
            BookingsORM.date_from <= date_to,
            BookingsORM.date_to >= date_from
        )
        .group_by(BookingsORM.room_id)
        .cte(name="rooms_booked_data")
    )

    rooms_left_data = (
        select(
            RoomsORM.id.label("room_id"),
            (RoomsORM.quantity - func.coalesce(rooms_booked_data.c.count_rooms_booked, 0)).label("rooms_left")
        )
        .select_from(RoomsORM)
        .outerjoin(rooms_booked_data, RoomsORM.id == rooms_booked_data.c.room_id)
        .cte(name="rooms_left_data")
    )

    rooms_ids_for_hotel = (
        select(RoomsORM.id)
        .select_from(RoomsORM)
    )
    if hotel_id is not None:
        rooms_ids_for_hotel =  rooms_ids_for_hotel.filter_by(hotel_id=hotel_id)

    # rooms_ids_for_hotel = rooms_ids_for_hotel.subquery(name="rooms_ids_for_hotel")

    rooms_ids_to_get = (
        select(rooms_left_data.c.room_id)
        .select_from(rooms_left_data)
        .filter(
            rooms_left_data.c.rooms_left > 0,
            rooms_left_data.c.room_id.in_(rooms_ids_for_hotel),
        )
    )

    # print(rooms_ids_to_get.compile(bind=engine,compile_kwargs={"literal_binds": True }))

    return rooms_ids_to_get
