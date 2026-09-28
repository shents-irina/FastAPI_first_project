from exceptions import (
    FacilityAlreadyExistsException,
    FacilityNotFoundException,
    ObjectAlreadyExistsException,
    ObjectNotFoundException,
)
from schemas.facilities import Facility, FacilityAdd
from services.base import BaseService


class FacilityService(BaseService):
    async def get_facility_with_check(self, facility_id: int) -> Facility:
        try:
            return await self.db.facilities.get_one(id=facility_id)
        except ObjectNotFoundException as exc:
            raise FacilityNotFoundException from exc

    async def get_facilities(self):
        return await self.db.facilities.get_all()

    async def create_facility(self, facility_data: FacilityAdd):
        try:
            facility = await self.db.facilities.add(facility_data)
            await self.db.commit()
        except ObjectAlreadyExistsException as exc:
            raise FacilityAlreadyExistsException from exc
        return facility

    async def delete_facility(self, facility_id: int):
        await self.get_facility_with_check(facility_id)
        await self.db.facilities.delete(id=facility_id)
        await self.db.commit()
