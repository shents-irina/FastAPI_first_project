import json

from fastapi import APIRouter, Body

from api.dependencies import DBDep
from init import redis_manager
from schemas.facilities import FacilityAdd


router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get(path="", summary="Получение всех видов удобств")
async def get_facilities(db: DBDep):
    facilities_from_cache = await redis_manager.get("facilities")
    if not facilities_from_cache:
        facilities_schemas = await db.facilities.get_all()
        facilities_dicts: list[dict] = [f.model_dump() for f in facilities_schemas]
        facilities_json = json.dumps(facilities_dicts)
        await redis_manager.set("facilities", facilities_json, 10)
    else:
        facilities_dicts = json.loads(facilities_from_cache)
    return facilities_dicts


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
