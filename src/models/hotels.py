from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class HotelsORM(Base):
    __tablename__ = "hotels"
    __table_args__ = (UniqueConstraint("title", "location", name="uq_hotels_title_location"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    location: Mapped[str]
