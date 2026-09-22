from fastapi import APIRouter
from fastapi_cache.decorator import cache

from api.dependencies import DBDep
from schemas.facilities import FacilityAdd
from services.facilities import FacilityService

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get(path="", summary="Получение всех видов удобств")
@cache(expire=60)
async def get_facilities(db: DBDep):
    return await FacilityService(db).get_facilities()


@router.post(path="", summary="Добавление нового вида удобств")
async def create_facility(
    db: DBDep,
    facility_data: FacilityAdd,
):
    facility = await FacilityService(db).create_facility(facility_data)
    return {"status": "OK", "data": facility}


@router.delete(path="/{facility_id}", summary="Удаление данных удобства")
async def delete_facility(
    db: DBDep,
    facility_id: int,
):
    await FacilityService(db).delete_facility(facility_id)
    return {"status": "OK"}
