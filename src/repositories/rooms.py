from models.rooms import RoomsORM
from repositories.base import BaseRepository


class RoomsRepository(BaseRepository):
    model = RoomsORM
