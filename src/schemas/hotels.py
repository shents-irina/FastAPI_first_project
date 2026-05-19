from pydantic import BaseModel, Field


class Hotel(BaseModel):
    title: str
    location: str


class HotelPatch(BaseModel):
    title: str | None = None
    location: str | None = None