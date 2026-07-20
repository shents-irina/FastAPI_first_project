from models.facilities import FacilitiesORM
from repositories.base import BaseRepository
from schemas.facilities import Facility


class FacilitiesRepository(BaseRepository):
    model = FacilitiesORM
    schema = Facility
