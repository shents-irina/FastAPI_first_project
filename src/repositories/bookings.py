from models.bookings import BookingsORM
from repositories.base import BaseRepository
from schemas.bookings import Booking


class BookingsRepository(BaseRepository):
    model = BookingsORM
    schema = Booking
