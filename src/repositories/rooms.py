from pydantic import BaseModel
from sqlalchemy import insert, select

from models.rooms import RoomsORM
from repositories.base import BaseRepository
from schemas.rooms import Room, RoomAdd


class RoomsRepository(BaseRepository):
    model = RoomsORM
    schema = Room
