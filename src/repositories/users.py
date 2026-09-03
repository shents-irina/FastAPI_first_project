from pydantic import EmailStr
from sqlalchemy import select

from models.users import UsersORM
from repositories.base import BaseRepository
from repositories.mappers.mappers import UserDataMapper
from schemas.users import User, UserWithHashedPassword


class UsersRepository(BaseRepository[UsersORM, User]):
    model = UsersORM
    mapper = UserDataMapper

    async def get_user_with_hashed_password(self, email: EmailStr):
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return UserWithHashedPassword.model_validate(model, from_attributes=True)
