from sqlalchemy import func, select

from models.hotels import HotelsORM
from repositories.base import BaseRepository
from schemas.hotels import Hotel


class HotelsRepository(BaseRepository):
    model = HotelsORM
    schema = Hotel

    async def get_all(
        self,
        title,
        location,
        offset,
        limit
    ) -> list[Hotel]:
        query = select(HotelsORM)
        if location:
            query = query.filter(func.lower(HotelsORM.location).contains(location.strip().lower()))
        if title:
            query = query.filter(func.lower(HotelsORM.title).contains(title.strip().lower()))
        query = (
            query
            .offset(offset)
            .limit(limit)
        )
        # print(query.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)

        return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]
