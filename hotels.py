from fastapi import Query, Body, APIRouter
from schemas.hotels import Hotel, HotelPatch

router = APIRouter(prefix='/hotels', tags=['Отели'])

hotels = [
    {"id": 1, "title": "Sochi1", "name": "sochi"},
    {"id": 2, "title": "Dubai", "name": "dubai"},
    {"id": 3, "title": "Sochi", "name": "sochi_"},
]


@router.get(path="", summary="Получение данных отеля")
def get_hotels(
    id: int | None = Query(default=None, description="айдишник"),
    title: str | None = Query(default=None, description="название отеля"),
):
    if not id and not title:
        return hotels
    return [hotel for hotel in hotels if hotel["id"] == id or hotel["title"] == title]


@router.delete(path="/{hotel_id}", summary="Удаление данных отеля")
def delete_hotels(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {"status": "OK"}


@router.post(
    path= "",
    summary="Регистрирует новый отель",
    description="Довавляет данные нового отеля",
)
def create_hotel(hotel_data: Hotel):
    global hotels
    hotels.append(
        {
            "id": hotels[-1]["id"] + 1,
            "title": hotel_data.title
        }
    )
    return {"status": "OK"}


@router.put(
    path="/{hotel_id}",
    summary="Замена данных отеля",
    description="Полная замена всех данных",
)
def edit_hotel(
    hotel_id: int,
    hotel_data: Hotel
):
    global hotels
    hotel = next(hotel for hotel in hotels if hotel["id"] == hotel_id)
    hotel["title"] = hotel_data.title
    hotel["name"] = hotel_data.name
    return {"status": "OK"}


@router.patch(
    path="/{hotel_id}",
    summary="Частичная замена данных отеля",
    description="Заменяем какие-то конкретные данные",
)
def partial_edit(
    hotel_id: int,
    hotel_data: HotelPatch
):
    global hotels
    hotel = next(hotel for hotel in hotels if hotel["id"] == hotel_id)
    if hotel_data.title:
        hotel["title"] = hotel_data.title
    if hotel_data.name:
        hotel["name"] = hotel_data.name
    return {"status": "OK"}