from typing import Annotated

from fastapi import Depends, Request

from database import async_session_maker
from exceptions import (
    ExpiredTokenException,
    ExpiredTokenHTTPException,
    IncorrectTokenException,
    IncorrectTokenHTTPException,
    NoAccessTokenHTTPException,
)
from schemas.pagination import PaginationParams
from services.auth import AuthService
from utils.db_manager import DBManager

PaginationDep = Annotated[PaginationParams, Depends()]


def get_token(request: Request) -> str:
    """Извлекает токен доступа из cookie ``access_token``.

    :raises NoAccessTokenHTTPException: Если cookie ``access_token`` отсутствует или пуста. HTTP-статус: 401.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise NoAccessTokenHTTPException
    return token


def get_current_user_id(token: str = Depends(get_token)) -> int:
    """Проверяет токен и возвращает идентификатор текущего пользователя.

    :raises ExpiredTokenHTTPException: Если срок действия токена истёк. HTTP-статус: 401.
    :raises IncorrectTokenHTTPException: Если токен некорректен или поле ``user_id`` отсутствует. HTTP-статус: 401.
    """
    try:
        data = AuthService.decode_token(token)
    except ExpiredTokenException as exc:
        raise ExpiredTokenHTTPException from exc
    except IncorrectTokenException as exc:
        raise IncorrectTokenHTTPException from exc

    user_id = data.get("user_id")
    if not user_id:
        raise IncorrectTokenHTTPException
    return user_id


UserIdDep = Annotated[int, Depends(get_current_user_id)]


async def get_db():
    """Предоставляет менеджер базы данных для обработки запроса.

    При завершении зависимости закрывает сессию базы данных.
    """
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]
