from fastapi import APIRouter, Body
from fastapi_cache.decorator import cache

from api.dependencies import DBDep
from schemas.facilities import FacilityAdd


router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get(path="", summary="Получение всех видов удобств")
@cache(expire=60)
async def get_facilities(db: DBDep):
    return await db.facilities.get_all()


@router.post(path="", summary="Добавление нового вида удобств")
async def create_facility(
    db: DBDep,
    facility_data: FacilityAdd = Body(),
):
    facility = await db.facilities.add(facility_data)
    await db.commit()
    return {"status": "OK", "data": facility}


@router.delete(path="/{facility_id}", summary="Удаление данных удобства")
async def delete_facility(
    db: DBDep,
    facility_id: int,
):
    await db.facilities.delete(id=facility_id)
    await db.commit()
    return {"status": "OK"}
