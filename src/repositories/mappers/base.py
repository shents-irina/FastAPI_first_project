from pydantic import BaseModel

from database import Base


class DataMapper[DBModelType: Base, SchemaType: BaseModel]:
    """Преобразует данные между ORM-моделью и pydantic-схемой.

    Дочерний класс указывает, какую пару ``db_model`` и ``schema`` он связывает.
    """

    db_model: type[DBModelType]
    schema: type[SchemaType]

    @classmethod
    def map_to_domain_entity(cls, data: DBModelType) -> SchemaType:
        """Преобразует ORM-объект в pydantic-схему.

        :param data: Объект ORM-модели.
        :return: Схема с данными объекта.
        """
        return cls.schema.model_validate(data, from_attributes=True)

    @classmethod
    def map_to_persistence_entity(cls, data: SchemaType) -> DBModelType:
        """Преобразует pydantic-схему в ORM-объект.

        :param data: Схема с данными.
        :return: Новый объект ORM-модели.
        """
        return cls.db_model(**data.model_dump())
