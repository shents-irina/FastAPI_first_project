from pydantic import BaseModel, Field

from schemas.facilities import Facility


class RoomAddRequest(BaseModel):
    title: str
    description: str | None = None
    price: int = Field(ge=0)
    quantity: int = Field(ge=0)
    facilities_ids: set[int] = set()


class RoomAdd(BaseModel):
    hotel_id: int
    title: str
    description: str | None = None
    price: int = Field(ge=0)
    quantity: int = Field(ge=0)


class Room(RoomAdd):
    id: int


class RoomWithRels(Room):
    facilities: list[Facility]


class RoomPatchRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = Field(default=None, ge=0)
    quantity: int | None = Field(default=None, ge=0)
    facilities_ids: set[int] = set()


class RoomPatch(BaseModel):
    hotel_id: int | None = None
    title: str | None = None
    description: str | None = None
    price: int | None = Field(default=None, ge=0)
    quantity: int | None = Field(default=None, ge=0)
