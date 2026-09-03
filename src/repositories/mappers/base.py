from pydantic import BaseModel

from database import Base


class DataMapper[DBModelType: Base, SchemaType: BaseModel]:
    db_model: type[DBModelType]
    schema: type[SchemaType]

    @classmethod
    def map_to_domain_entity(cls, data: DBModelType) -> SchemaType:
        return cls.schema.model_validate(data, from_attributes=True)

    @classmethod
    def map_to_persistence_entity(cls, data: SchemaType) -> DBModelType:
        return cls.db_model(**data.model_dump())
