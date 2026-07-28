from models.hotels import HotelsORM
from repositories.mappers.base import DataMapper
from schemas.hotels import Hotel


class HotelDataMapper(DataMapper):
    db_model = HotelsORM
    schema = Hotel
