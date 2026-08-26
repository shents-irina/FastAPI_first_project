from datetime import date

from sqlalchemy import select, func

from models.bookings import BookingsORM
from models.rooms import RoomsORM


def rooms_ids_for_booking(
    date_from: date,
    date_to: date,
    hotel_id : int | None = None,
):
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

    rooms_ids_to_get = (
        select(rooms_left_data.c.room_id)
        .select_from(rooms_left_data)
        .filter(
            rooms_left_data.c.rooms_left > 0,
            rooms_left_data.c.room_id.in_(rooms_ids_for_hotel),
        )
    )

    return rooms_ids_to_get
