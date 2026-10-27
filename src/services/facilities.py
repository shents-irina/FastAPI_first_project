import logging

from exceptions import (
    FacilityAlreadyExistsException,
    FacilityNotFoundException,
    ObjectAlreadyExistsException,
    ObjectNotFoundException,
)
from schemas.facilities import Facility, FacilityAdd
from services.base import BaseService

logger = logging.getLogger(__name__)


class FacilityService(BaseService):
    """Сервис удобств: просмотр, создание и удаление."""

    async def get_facility_with_check(self, facility_id: int) -> Facility:
        """Возвращает удобство по идентификатору.

        :raises FacilityNotFoundException: Удобства с таким id нет.
        """
        try:
            return await self.db.facilities.get_one(id=facility_id)
        except ObjectNotFoundException as exc:
            raise FacilityNotFoundException from exc

    async def get_facilities(self):
        """Возвращает список всех удобств."""
        return await self.db.facilities.get_all()

    async def create_facility(self, facility_data: FacilityAdd):
        """Создаёт удобство и возвращает его вместе с присвоенным id.

        :raises FacilityAlreadyExistsException: Удобство с таким названием уже существует.
        """
        try:
            facility = await self.db.facilities.add(facility_data)
            await self.db.commit()
        except ObjectAlreadyExistsException as exc:
            raise FacilityAlreadyExistsException from exc
        logger.info("Создано удобство facility_id=%s", facility.id)
        return facility

    async def delete_facility(self, facility_id: int):
        """Удаляет удобство.

        :raises FacilityNotFoundException: Удобства с таким id нет.
        """
        await self.get_facility_with_check(facility_id)
        await self.db.facilities.delete(id=facility_id)
        await self.db.commit()
        logger.info("Удобство удалено facility_id=%s", facility_id)
