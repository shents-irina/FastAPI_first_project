import sqlalchemy.exc
from pydantic import EmailStr
from sqlalchemy import select

from exceptions import ObjectNotFoundException
from models.users import UsersORM
from repositories.base import BaseRepository
from repositories.mappers.mappers import UserDataMapper
from schemas.users import User, UserWithHashedPassword


class UsersRepository(BaseRepository[UsersORM, User]):
    """Репозиторий пользователей."""

    model = UsersORM
    mapper = UserDataMapper

    async def get_user_with_hashed_password(self, email: EmailStr) -> UserWithHashedPassword:
        """Возвращает пользователя вместе с хэшем пароля.

        В отличие от схемы ``User``, результат содержит хэш пароля.
        Метод нужен для проверки пароля при входе.
        Не передавайте результат в ответы API.

        :param email: Email пользователя.
        :return: Данные пользователя вместе с хэшем пароля.
        :raises ObjectNotFoundException: Если пользователь с таким email не найден.
        """
        query = select(self.model).filter_by(email=email)
        try:
            result = await self.session.execute(query)
            model = result.scalar_one()
        except sqlalchemy.exc.NoResultFound as exc:
            raise ObjectNotFoundException from exc
        return UserWithHashedPassword.model_validate(model, from_attributes=True)
