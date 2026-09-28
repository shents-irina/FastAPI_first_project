from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models import FacilitiesORM, HotelsORM


class RoomsORM(Base):
    __tablename__ = "rooms"
    __table_args__ = (UniqueConstraint("hotel_id", "title", name="uq_rooms_hotel_id_title"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id", ondelete="CASCADE"))
    title: Mapped[str]
    description: Mapped[str | None]
    price: Mapped[int]
    quantity: Mapped[int]

    facilities: Mapped[list["FacilitiesORM"]] = relationship(
        back_populates="rooms", secondary="rooms_facilities"
    )
    hotel: Mapped["HotelsORM"] = relationship()
