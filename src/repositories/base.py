from collections.abc import Sequence
import logging

import sqlalchemy.exc
from asyncpg.exceptions import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update

from database import Base
from exceptions import ObjectAlreadyExistsException, ObjectNotFoundException
from repositories.mappers.base import DataMapper

logger = logging.getLogger(__name__)


class BaseRepository[ModelType: Base, SchemaType: BaseModel]:
    model: type[ModelType]
    mapper: type[DataMapper[ModelType, SchemaType]]

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filter, **filter_by) -> list[SchemaType]:
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_all(self, *args, **kwargs) -> list[SchemaType]:
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by) -> SchemaType | None:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def get_one(self, **filter_by) -> SchemaType:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except sqlalchemy.exc.NoResultFound:
            raise ObjectNotFoundException
        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel) -> SchemaType:
        add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        try:
            result = await self.session.execute(add_data_stmt)
            model = result.scalars().one()
        except sqlalchemy.exc.IntegrityError as exc:
            if exc.orig is not None and isinstance(exc.orig.__cause__, UniqueViolationError):
                logger.warning("Попытка добавить уже существующую запись: %s", exc.orig)
                raise ObjectAlreadyExistsException from exc
            else:
                logger.exception("Не удалось добавить данные в БД: неизвестная ошибка целостности")
                raise
        return self.mapper.map_to_domain_entity(model)

    async def add_bulk(self, data: Sequence[BaseModel]) -> None:
        add_data_stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(add_data_stmt)

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )
        await self.session.execute(update_stmt)

    async def delete(self, *filter, **filter_by) -> None:
        delete_stmt = delete(self.model).filter(*filter).filter_by(**filter_by)
        await self.session.execute(delete_stmt)
