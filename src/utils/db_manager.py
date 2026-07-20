from repositories.bookings import BookingsRepository
from repositories.facilities import FacilitiesRepository, RoomsFacilitiesRepository
from repositories.hotels import HotelsRepository
from repositories.rooms import RoomsRepository
from repositories.users import UsersRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UsersRepository(self.session)
        self.hotels = HotelsRepository(self.session)
        self.rooms = RoomsRepository(self.session)
        self.bookings = BookingsRepository(self.session)
        self.facilities = FacilitiesRepository(self.session)
        self.rooms_facilities = RoomsFacilitiesRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.rollback( )
        await self.session.close()

    async def commit(self):
        await self.session.commit()
