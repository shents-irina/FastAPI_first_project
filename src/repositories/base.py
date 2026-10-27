import logging
from collections.abc import Sequence
from typing import NoReturn

import sqlalchemy.exc
from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update

from database import Base
from exceptions import ObjectAlreadyExistsException, ObjectIsInUseException, ObjectNotFoundException
from repositories.mappers.base import DataMapper

logger = logging.getLogger(__name__)


class BaseRepository[ModelType: Base, SchemaType: BaseModel]:
    """Предоставляет типовые операции чтения и изменения записей одной модели.

    Результаты чтения и добавления преобразуются маппером в Pydantic-схемы ``SchemaType``.

    Репозиторий не фиксирует транзакцию: ``commit()`` вызывается внешним кодом.
    """

    model: type[ModelType]
    mapper: type[DataMapper[ModelType, SchemaType]]

    def __init__(self, session):
        self.session = session

    def _raise_for_write_integrity_error(self, exc: sqlalchemy.exc.IntegrityError) -> NoReturn:
        """Преобразует распознанную ошибку целостности в доменное исключение.

        Тип нарушения определяется по исключению ``asyncpg`` в ``exc.orig.__cause__``.
        Нераспознанные ошибки пробрасываются без преобразования.
        Метод всегда завершается исключением.

        :raises ObjectAlreadyExistsException: Если распознано нарушение ограничения уникальности.
        :raises ObjectNotFoundException: Если указан идентификатор несуществующей связанной записи.
        :raises sqlalchemy.exc.IntegrityError: Если ошибка целостности не распознана.
        """
        if exc.orig is not None and isinstance(exc.orig.__cause__, UniqueViolationError):
            logger.warning("Запись с такими уникальными полями уже существует: %s", exc.orig)
            raise ObjectAlreadyExistsException from exc
        if exc.orig is not None and isinstance(exc.orig.__cause__, ForeignKeyViolationError):
            logger.warning("Ссылка на несуществующий связанный объект: %s", exc.orig)
            raise ObjectNotFoundException from exc
        logger.exception("Не удалось выполнить операцию с БД: неизвестная ошибка целостности")
        raise exc

    async def get_filtered(self, *filter, **filter_by) -> list[SchemaType]:
        """Возвращает записи, соответствующие условиям фильтрации.

        Без условий возвращает все записи.

        :return: Список Pydantic-схем или пустой список, если подходящих записей нет.
        """
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_all(self) -> list[SchemaType]:
        """Возвращает все записи в виде списка Pydantic-схем."""
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by) -> SchemaType | None:
        """Возвращает одну подходящую запись или ``None``.

        Именованные аргументы задают условия равенства по атрибутам модели.

        :raises sqlalchemy.exc.MultipleResultsFound: Если условиям соответствует больше одной записи.
        """
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def get_one(self, **filter_by) -> SchemaType:
        """Возвращает единственную запись, соответствующую условиям.

        Именованные аргументы задают условия равенства по атрибутам модели.

        :raises ObjectNotFoundException: Если подходящая запись не найдена.
        :raises sqlalchemy.exc.MultipleResultsFound: Если условиям соответствует больше одной записи.
        """
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except sqlalchemy.exc.NoResultFound as exc:
            raise ObjectNotFoundException from exc
        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel) -> SchemaType:
        """Добавляет запись и возвращает её в виде Pydantic-схемы.

        :param data: Данные создаваемой записи.
        :raises ObjectAlreadyExistsException: Если распознано нарушение ограничения уникальности.
        :raises ObjectNotFoundException: Если указан идентификатор несуществующей связанной записи.
        :raises sqlalchemy.exc.IntegrityError: Если ошибка целостности не распознана.
        """
        add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        try:
            result = await self.session.execute(add_data_stmt)
            model = result.scalars().one()
        except sqlalchemy.exc.IntegrityError as exc:
            self._raise_for_write_integrity_error(exc)
        return self.mapper.map_to_domain_entity(model)

    async def add_bulk(self, data: Sequence[BaseModel]) -> None:
        """Вставляет сразу много записей одним запросом.

        Если передана пустая последовательность, запрос не выполняется.

        :param data: Последовательность данных создаваемых записей.
        :raises ObjectAlreadyExistsException: Если распознано нарушение ограничения уникальности.
        :raises ObjectNotFoundException: Если указан идентификатор несуществующей связанной записи.
        :raises sqlalchemy.exc.IntegrityError: Если ошибка целостности не распознана.
        """
        if not data:
            return
        add_data_stmt = insert(self.model).values([item.model_dump() for item in data])
        try:
            await self.session.execute(add_data_stmt)
        except sqlalchemy.exc.IntegrityError as exc:
            self._raise_for_write_integrity_error(exc)

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        """Обновляет записи, соответствующие условиям равенства.

        Без условий ``filter_by`` обновляет все записи.
        Если нет полей для обновления ``data``, запрос не выполняется.

        :param data: Новые значения полей.
        :param exclude_unset: Определяет, какие поля из ``data`` попадут в обновление.
            Если ``True``, обновляются только поля, которые были явно переданы при создании ``data``
            Если ``False`` (по умолчанию), обновляются все поля ``data`` (все поля должны быть переданы).
        :raises ObjectAlreadyExistsException: Если распознано нарушение ограничения уникальности.
        :raises ObjectNotFoundException: Если указан идентификатор несуществующей связанной записи.
        :raises sqlalchemy.exc.IntegrityError: Если ошибка целостности не распознана.
        """
        values = data.model_dump(exclude_unset=exclude_unset)
        if not values:
            return
        update_stmt = update(self.model).filter_by(**filter_by).values(**values)
        try:
            await self.session.execute(update_stmt)
        except sqlalchemy.exc.IntegrityError as exc:
            self._raise_for_write_integrity_error(exc)

    async def delete(self, *filter, **filter_by) -> None:
        """Удаляет записи, соответствующие условиям фильтрации.

        Без условий удаляет все записи.

        :raises ObjectIsInUseException: Если на запись ссылаются другие таблицы
        :raises sqlalchemy.exc.IntegrityError: Если ошибка целостности не распознана.
        """
        delete_stmt = delete(self.model).filter(*filter).filter_by(**filter_by)
        try:
            await self.session.execute(delete_stmt)
        except sqlalchemy.exc.IntegrityError as exc:
            if exc.orig is not None and isinstance(exc.orig.__cause__, ForeignKeyViolationError):
                logger.warning("Попытка удалить объект, на который есть ссылки: %s", exc.orig)
                raise ObjectIsInUseException from exc
            logger.exception("Не удалось удалить данные из БД: неизвестная ошибка целостности")
            raise
