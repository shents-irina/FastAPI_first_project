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


class UserDataMapper(DataMapper[UsersORM, User]):
    db_model = UsersORM
    schema = User


class HotelDataMapper(DataMapper[HotelsORM, Hotel]):
    db_model = HotelsORM
    schema = Hotel


class RoomDataMapper(DataMapper[RoomsORM, Room]):
    db_model = RoomsORM
    schema = Room


class RoomWithRelsDataMapper(DataMapper[RoomsORM, RoomWithRels]):
    db_model = RoomsORM
    schema = RoomWithRels


class BookingDataMapper(DataMapper[BookingsORM, Booking]):
    db_model = BookingsORM
    schema = Booking


class FacilityDataMapper(DataMapper[FacilitiesORM, Facility]):
    db_model = FacilitiesORM
    schema = Facility


class RoomFacilityDataMapper(DataMapper[RoomsFacilitiesORM, RoomFacility]):
    db_model = RoomsFacilitiesORM
    schema = RoomFacility
