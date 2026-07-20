from models.facilities import FacilitiesORM, RoomsFacilitiesORM
from repositories.base import BaseRepository
from schemas.facilities import Facility, RoomFacility


class FacilitiesRepository(BaseRepository):
    model = FacilitiesORM
    schema = Facility


class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesORM
    schema = RoomFacility
