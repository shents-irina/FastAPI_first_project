from models.bookings import BookingsORM
from models.facilities import FacilitiesORM, RoomsFacilitiesORM
from models.hotels import HotelsORM
from models.rooms import RoomsORM
from models.users import UsersORM
from repositories.mappers.base import DataMapper
from schemas.bookings import Booking
from schemas.facilities import Facility, RoomFacility
from schemas.hotels import Hotel
from schemas.rooms import Room, RoomWithRels
from schemas.users import User


class UserDataMapper(DataMapper):
    db_model = UsersORM
    schema = User


class HotelDataMapper(DataMapper):
    db_model = HotelsORM
    schema = Hotel


class RoomDataMapper(DataMapper):
    db_model = RoomsORM
    schema = Room


class RoomWithRelsDataMapper(DataMapper):
    db_model = RoomsORM
    schema = RoomWithRels


class BookingDataMapper(DataMapper):
    db_model = BookingsORM
    schema = Booking


class FacilityDataMapper(DataMapper):
    db_model = FacilitiesORM
    schema = Facility


class RoomFacilityDataMapper(DataMapper):
    db_model = RoomsFacilitiesORM
    schema = RoomFacility
