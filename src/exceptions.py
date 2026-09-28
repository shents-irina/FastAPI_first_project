from datetime import UTC, date, datetime

from fastapi import HTTPException


class AppException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, detail: str | None = None, *args):
        if detail:
            self.detail = detail
        super().__init__(self.detail, *args)


class AuthException(AppException):
    detail = "Ошибка аутентификации"


class EmailNotRegisteredException(AuthException):
    detail = "Пользователь с таким email не зарегистрирован"


class IncorrectTokenException(AuthException):
    detail = "Некорректный токен доступа"


class ExpiredTokenException(AuthException):
    detail = "Срок действия токена истёк"


class IncorrectPasswordException(AuthException):
    detail = "Пароль неверный"


class ObjectNotFoundException(AppException):
    detail = "Объект не найден"


class HotelNotFoundException(ObjectNotFoundException):
    detail = "Отель не найден"


class RoomNotFoundException(ObjectNotFoundException):
    detail = "Номер не найден"


class BookingNotFoundException(ObjectNotFoundException):
    detail = "Бронирование не найдено"


class FacilityNotFoundException(ObjectNotFoundException):
    detail = "Удобство не найдено"


class ObjectAlreadyExistsException(AppException):
    detail = "Похожий объект уже существует"


class HotelAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Похожий отель уже существует"


class RoomAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Похожий номер уже существует"


class FacilityAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Похожее удобство уже существует"


class UserAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Пользователь уже существует"


class ObjectIsInUseException(AppException):
    detail = "Объект используется в других записях"


class AllRoomsAreBookedException(AppException):
    detail = "Не осталось свободных номеров на выбранные даты"


class CheckOutBeforeCheckInException(AppException):
    detail = "Дата выезда не может быть раньше даты заезда"


class BookingAlreadyStartedException(AppException):
    detail = "Нельзя отменить бронирование после даты заезда"


class BookingDateInPastException(AppException):
    detail = "Нельзя забронировать номер на прошедшую дату"


def check_date_to_after_date_from(date_from: date, date_to: date) -> None:
    if date_to <= date_from:
        raise CheckOutBeforeCheckInException()


def check_booking_not_started(date_from: date) -> None:
    if date_from <= datetime.now(tz=UTC).date():
        raise BookingAlreadyStartedException()


def check_booking_not_in_past(date_from: date) -> None:
    if date_from < datetime.now(tz=UTC).date():
        raise BookingDateInPastException()


class AppHTTPException(HTTPException):
    status_code = 500
    detail = None

    def __init__(self, detail: str | None = None):
        super().__init__(status_code=self.status_code, detail=detail or self.detail)


class AuthHTTPException(AppHTTPException):
    status_code = 401
    detail = "Ошибка аутентификации"


class EmailNotRegisteredHTTPException(AuthHTTPException):
    detail = "Пользователь с таким email не зарегистрирован"


class IncorrectPasswordHTTPException(AuthHTTPException):
    detail = "Пароль неверный"


class NoAccessTokenHTTPException(AuthHTTPException):
    detail = "Вы не предоставили токен доступа"


class IncorrectTokenHTTPException(AuthHTTPException):
    detail = "Некорректный токен доступа"


class ExpiredTokenHTTPException(AuthHTTPException):
    detail = "Срок действия токена истёк"


class ObjectNotFoundHTTPException(AppHTTPException):
    status_code = 404
    detail = "Объект не найден"


class HotelNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Отель не найден"


class RoomNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Номер не найден"


class BookingNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Бронирование не найдено"


class FacilityNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Удобство не найдено"


class ObjectAlreadyExistsHTTPException(AppHTTPException):
    status_code = 409
    detail = "Похожий объект уже существует"


class HotelAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    detail = "Похожий отель уже существует"


class RoomAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    detail = "Похожий номер уже существует"


class FacilityAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    detail = "Похожее удобство уже существует"


class UserAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    detail = "Пользователь с такой почтой уже существует"


class ObjectIsInUseHTTPException(AppHTTPException):
    status_code = 409
    detail = "Объект используется в других записях"


class AllRoomsAreBookedHTTPException(AppHTTPException):
    status_code = 409
    detail = "Не осталось свободных номеров на выбранные даты"


class CheckOutBeforeCheckInHTTPException(AppHTTPException):
    status_code = 422
    detail = "Дата выезда не может быть раньше даты заезда"


class BookingAlreadyStartedHTTPException(AppHTTPException):
    status_code = 409
    detail = "Нельзя отменить бронирование после даты заезда"


class BookingDateInPastHTTPException(AppHTTPException):
    status_code = 422
    detail = "Нельзя забронировать номер на прошедшую дату"
