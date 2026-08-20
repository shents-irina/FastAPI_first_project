from datetime import date

from schemas.bookings import BookingAdd


async def test_booking_crud(db):
    user_id = (await db.users.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id

    # создать бронь
    booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        date_from=date(year=2026, month=8, day=1),
        date_to=date(year=2026, month=8, day=5),
        price=1000,
    )
    new_booking = await db.bookings.add(booking_data)

    # получить эту бронь и убедиться, что она есть
    booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert booking
    assert booking.id == new_booking.id
    assert booking.room_id == new_booking.room_id
    assert booking.user_id == new_booking.user_id

    # обновить бронь
    update_date = date(year=2026, month=8, day=10)
    update_booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        date_from=date(year=2026, month=8, day=1),
        date_to=update_date,
        price=1000,
    )
    await db.bookings.edit(update_booking_data, id=new_booking.id)
    update_booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert update_booking
    assert update_booking.id == new_booking.id
    assert update_booking.date_to == update_date

    # удалить бронь
    await db.bookings.delete(id=new_booking.id)
    booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert not booking
