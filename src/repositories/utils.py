from datetime import date

from sqlalchemy import func, select

from models.bookings import BookingsORM
from models.rooms import RoomsORM


def rooms_ids_for_booking(
    date_from: date,
    date_to: date,
    hotel_id: int | None = None,
):
    """Строит запрос идентификаторов номеров, доступных для бронирования.

    Запрос только строится и не выполняется.
    Номер считается доступным, если число бронирований, пересекающихся с периодом, меньше его ``quantity``.
    Пересечением считается любое бронирование, у которого ``date_from <= date_to`` периода и ``date_to >= date_from`` периода.

    :param date_from: Начало периода.
    :param date_to: Конец периода.
    :param hotel_id: Идентификатор отеля. Если указан, выбираются только номера этого отеля, иначе номера всех отелей.
    :return: Запрос ``Select``, возвращающий идентификаторы доступных номеров.
        Его можно выполнить или использовать как подзапрос в ``in_()``.
    """
    #  Для каждого номера считаем, сколько бронирований пересекается с запрошенным периодом.
    rooms_booked_data = (
        select(BookingsORM.room_id, func.count().label("count_rooms_booked"))
        .select_from(BookingsORM)
        .filter(BookingsORM.date_from <= date_to, BookingsORM.date_to >= date_from)
        .group_by(BookingsORM.room_id)
        .cte(name="rooms_booked_data")
    )

    # Считаем остаток по каждому номеру: quantity минус число броней.
    # outerjoin сохраняет номера, у которых нет броней в периоде,
    # для них count_rooms_booked равен NULL, и coalesce заменяет его на 0.
    rooms_left_data = (
        select(
            RoomsORM.id.label("room_id"),
            (RoomsORM.quantity - func.coalesce(rooms_booked_data.c.count_rooms_booked, 0)).label(
                "rooms_left"
            ),
        )
        .select_from(RoomsORM)
        .outerjoin(rooms_booked_data, RoomsORM.id == rooms_booked_data.c.room_id)
        .cte(name="rooms_left_data")
    )

    # Определяем, из каких номеров выбирать: все номера или только номера указанного отеля.
    rooms_ids_for_hotel = select(RoomsORM.id).select_from(RoomsORM)
    if hotel_id is not None:
        rooms_ids_for_hotel = rooms_ids_for_hotel.filter_by(hotel_id=hotel_id)

    # Оставляем номера с положительным остатком из нужного отеля.
    rooms_ids_to_get = (
        select(rooms_left_data.c.room_id)
        .select_from(rooms_left_data)
        .filter(
            rooms_left_data.c.rooms_left > 0,
            rooms_left_data.c.room_id.in_(rooms_ids_for_hotel),
        )
    )

    # Возвращаем незавершённый запрос; выполняет его вызывающий код.
    return rooms_ids_to_get
