from datetime import date

from fastapi import HTTPException


class AppException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args):
        super().__init__(self.detail, *args)


class ObjectNotFoundException(AppException):
    detail = "Объект не найден"


class ObjectAlreadyExistsException(AppException):
    detail = "Похожий объект уже существует"


class AllRoomsAreBookedException(AppException):
    detail = "Не осталось свободных номеров"


def check_date_to_after_date_from(date_from: date, date_to: date) -> bool:
    if date_to <= date_from:
        raise HTTPException(status_code=422, detail="Дата заезда не может быть позже даты выезда")
    return True


class AppHTTPException(HTTPException):
    status_code = 500
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class HotelNotFoundHTTPException(AppHTTPException):
    status_code = 404
    detail = "Отель не найден"


class RoomNotFoundHTTPException(AppHTTPException):
    status_code = 404
    detail = "Номер не найден"
