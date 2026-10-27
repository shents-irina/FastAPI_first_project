from fastapi import APIRouter, Response

from api.dependencies import DBDep, UserIdDep
from exceptions import (
    EmailNotRegisteredException,
    EmailNotRegisteredHTTPException,
    IncorrectPasswordException,
    IncorrectPasswordHTTPException,
    UserAlreadyExistsException,
    UserAlreadyExistsHTTPException,
)
from schemas.users import UserRequestAdd
from services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Аутентификация и авторизация"])


@router.post("/register")
async def register_user(
    data: UserRequestAdd,
    db: DBDep,
):
    """Регистрирует нового пользователя по email и паролю.

    :raises UserAlreadyExistsHTTPException: Если email уже зарегистрирован. HTTP-статус: 409.
    """
    try:
        await AuthService(db).register_user(data)
    except UserAlreadyExistsException as exc:
        raise UserAlreadyExistsHTTPException from exc
    return {"status": "OK"}


@router.post("/login")
async def login_user(
    data: UserRequestAdd,
    response: Response,
    db: DBDep,
):
    """Проверяет email и пароль и выдаёт JWT-токен.

    Токен возвращается в теле ответа и устанавливается в cookie ``access_token``.

    :raises EmailNotRegisteredHTTPException: Если email не зарегистрирован. HTTP-статус: 401.
    :raises IncorrectPasswordHTTPException: Если пароль неверный. HTTP-статус: 401.
    """
    try:
        access_token = await AuthService(db).login_user(data)
    except EmailNotRegisteredException as exc:
        raise EmailNotRegisteredHTTPException from exc
    except IncorrectPasswordException as exc:
        raise IncorrectPasswordHTTPException from exc

    response.set_cookie(key="access_token", value=access_token)

    return {"access_token": access_token}


@router.get("/me")
async def get_me(
    user_id: UserIdDep,
    db: DBDep,
):
    """Возвращает данные текущего пользователя.

    Требуется аутентификация.
    """
    user = await AuthService(db).get_me(user_id)
    return user


@router.post("/logout")
async def logout(user_id: UserIdDep, response: Response):
    """Удаляет cookie ``access_token`` для выхода из приложения.

    Требуется аутентификация.
    """
    response.delete_cookie(key="access_token")
    return {"status": "OK"}
