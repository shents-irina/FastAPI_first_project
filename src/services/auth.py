import logging
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from config import settings
from exceptions import (
    EmailNotRegisteredException,
    ExpiredTokenException,
    IncorrectPasswordException,
    IncorrectTokenException,
    ObjectAlreadyExistsException,
    ObjectNotFoundException,
    UserAlreadyExistsException,
)
from schemas.users import UserAdd, UserRequestAdd
from services.base import BaseService

logger = logging.getLogger(__name__)


class AuthService(BaseService):
    """Сервис аутентификации: пароли, токены доступа, регистрация и вход."""

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def create_access_token(data: dict) -> str:
        """Создаёт подписанный JWT-токен доступа.

        К копии ``data`` добавляется поле ``exp`` со временем истечения: текущее время UTC плюс ``settings.ACCESS_TOKEN_EXPIRE_MINUTES``.

        :param data: Данные для токена, например ``{"user_id": 1}``.
        :return: Закодированный токен в виде строки.
        """
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @classmethod
    def verify_password(cls, plain_password, hashed_password) -> bool:
        """Проверяет соответствует ли введенный пароль хэшу из БД.

        :param plain_password: Пароль в открытом виде.
        :param hashed_password: Хэш пароля из базы данных.
        :return: ``True``, если пароль верный, иначе ``False``
        """
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Возвращает хэш пароля для хранения в БД вместо пароля."""
        return cls.pwd_context.hash(password)

    @staticmethod
    def decode_token(token: str) -> dict:
        """Проверяет подпись и срок действия токена, возвращает его данные.

        :param token: JWT-токен доступа.
        :return: Данные токена, включая ``exp``.
        :raises ExpiredTokenException: Если срок действия токена истёк.
        :raises IncorrectTokenException: Если токен повреждён или подпись не совпадает.
        """
        try:
            return jwt.decode(
                jwt=token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError as exc:
            logger.debug("Токен доступа просрочен")
            raise ExpiredTokenException from exc
        except jwt.exceptions.DecodeError as exc:
            logger.warning("Получен некорректный токен доступа")
            raise IncorrectTokenException from exc

    async def register_user(self, data: UserRequestAdd):
        """Создаёт пользователя с хэшем пароля.

        :param data: Email и пароль в открытом виде.
        :raises UserAlreadyExistsException: Если пользователь с таким email уже существует.
        """
        hashed_password = self.hash_password(data.password)
        new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
        try:
            user = await self.db.users.add(new_user_data)
            await self.db.commit()
        except ObjectAlreadyExistsException as exc:
            raise UserAlreadyExistsException from exc
        logger.info("Зарегистрирован новый пользователь user_id=%s", user.id)

    async def login_user(self, data: UserRequestAdd) -> str:
        """Проверяет email с паролем и возвращает JWT-токен доступа.

        :param data: Email и пароль в открытом виде.
        :return: Токен доступа с ``user_id`` внутри.
        :raises EmailNotRegisteredException: Email не зарегистрирован.
        :raises IncorrectPasswordException: Пароль неверный.
        """
        try:
            user = await self.db.users.get_user_with_hashed_password(email=data.email)
        except ObjectNotFoundException as exc:
            logger.warning("Неудачный вход: email не зарегистрирован")
            raise EmailNotRegisteredException from exc
        if not self.verify_password(data.password, user.hashed_password):
            logger.warning("Неудачный вход: неверный пароль, user_id=%s", user.id)
            raise IncorrectPasswordException
        access_token = self.create_access_token({"user_id": user.id})

        logger.info("Успешный вход user_id=%s", user.id)
        return access_token

    async def get_me(self, user_id: int):
        """Возвращает данные пользователя по id или ``None``, если его нет в БД."""
        user = await self.db.users.get_one_or_none(id=user_id)
        return user
