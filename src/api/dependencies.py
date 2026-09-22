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
    token = request.cookies.get("access_token")
    if not token:
        raise NoAccessTokenHTTPException
    return token


def get_current_user_id(token: str = Depends(get_token)) -> int:
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
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]
