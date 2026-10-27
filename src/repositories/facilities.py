import sqlalchemy.exc
from sqlalchemy import delete, insert, select

from models.facilities import FacilitiesORM, RoomsFacilitiesORM
from repositories.base import BaseRepository
from repositories.mappers.mappers import FacilityDataMapper, RoomFacilityDataMapper
from schemas.facilities import Facility, RoomFacility


class FacilitiesRepository(BaseRepository[FacilitiesORM, Facility]):
    """Репозиторий удобств."""

    model = FacilitiesORM
    mapper = FacilityDataMapper


class RoomsFacilitiesRepository(BaseRepository[RoomsFacilitiesORM, RoomFacility]):
    """Репозиторий связей между номерами и удобствами."""

    model = RoomsFacilitiesORM
    mapper = RoomFacilityDataMapper

    async def set_room_facilities(self, room_id: int, facilities_ids: set[int]) -> None:
        """Приводит набор удобств номера к переданному.

        Сравнивает текущие связи номера с ``facilities_ids``: Лишние связи удаляются, недостающие добавляются, неизменные остаются нетронутыми.
        Пустой набор удаляет все связи номера.

        :param room_id: Идентификатор номера.
        :param facilities_ids: Идентификаторы удобств, которые должны остаться у номера.
        :raises ObjectNotFoundException: Если указан идентификатор несуществующего номера или удобства.
        """
        get_current_facilities_ids_query = select(self.model.facility_id).filter_by(room_id=room_id)
        result = await self.session.execute(get_current_facilities_ids_query)
        current_facilities_ids = set(result.scalars().all())
        ids_to_delete = current_facilities_ids - facilities_ids
        ids_to_insert = facilities_ids - current_facilities_ids

        if ids_to_delete:
            delete_m2m_facilities_stmt = delete(self.model).filter(
                self.model.room_id == room_id, self.model.facility_id.in_(ids_to_delete)
            )
            await self.session.execute(delete_m2m_facilities_stmt)

        if ids_to_insert:
            insert_m2m_facilities_stmt = insert(self.model).values(
                [{"room_id": room_id, "facility_id": f_id} for f_id in ids_to_insert]
            )
            try:
                await self.session.execute(insert_m2m_facilities_stmt)
            except sqlalchemy.exc.IntegrityError as exc:
                self._raise_for_write_integrity_error(exc)
