from pydantic import BaseModel

from models.facilities import FacilitiesORM, RoomsFacilitiesORM
from repositories.base import BaseRepository
from schemas.facilities import Facility, RoomFacility, RoomFacilityAdd


class FacilitiesRepository(BaseRepository):
    model = FacilitiesORM
    schema = Facility


class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesORM
    schema = RoomFacility

    async def edit_facilities(self, room_data: BaseModel, room_id: int):
        room_facilities_data = await self.get_filtered(room_id=room_id)   # список удобств, которые привязаны к room_id
        exist_f_ids = {data.facility_id for data in room_facilities_data}   # множество айдишников удобств, которые есть в базе
        query_f_ids = set(room_data.facilities_ids)  # превращаем данные из запроса в set

        new_f_ids_for_add = query_f_ids - exist_f_ids   # то, что нужно вставить
        f_ids_for_delete = exist_f_ids - query_f_ids   # то, что нужно удалить

        if new_f_ids_for_add:
            new_rooms_facilities_data = [RoomFacilityAdd(room_id=room_id, facility_id=f_id) for f_id in new_f_ids_for_add]   # новые схемы, которые нужно добавить в базу
            await self.add_bulk(new_rooms_facilities_data)
        await self.delete(RoomsFacilitiesORM.facility_id.in_(f_ids_for_delete), room_id=room_id)
