from models.bookings import BookingsORM
from repositories.base import BaseRepository
from repositories.mappers.mappers import BookingDataMapper


class BookingsRepository(BaseRepository):
    model = BookingsORM
    mapper = BookingDataMapper
