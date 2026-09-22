from schemas.facilities import FacilityAdd
from services.base import BaseService


class FacilityService(BaseService):
    async def get_facilities(self):
        return await self.db.facilities.get_all()

    async def create_facility(self, facility_data: FacilityAdd):
        facility = await self.db.facilities.add(facility_data)
        await self.db.commit()
        return facility

    async def delete_facility(self, facility_id: int):
        await self.db.facilities.delete(id=facility_id)
        await self.db.commit()
