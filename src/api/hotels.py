from typing import Annotated

from fastapi import APIRouter, Body, Query

from src.api.dependencies import PaginationDep
from src.schemas.hotels import Hotel, HotelPatch

router = APIRouter(prefix='/hotels', tags=['Отели'])

hotels = [
    {"id": 1, "title": "Сочи", "name": "sochi"},
    {"id": 2, "title": "Дубай", "name": "dubai"},
    {"id": 3, "title": "Мальдивы", "name": "maldives"},
    {"id": 4, "title": "Геленджик", "name": "gelendzhik"},
    {"id": 5, "title": "Москва", "name": "moscow"},
    {"id": 6, "title": "Казань", "name": "kazan"},
    {"id": 7, "title": "Санкт-Петербург", "name": "saint-petersburg"},
]


@router.get(path="", summary="Получение данных отеля")
def get_hotels(
    pagination: PaginationDep,
    id: int | None = Query(default=None, description="айдишник"),
    title: str | None = Query(default=None, description="название отеля"),
):
    hotels_ = []
    for hotel in hotels:
        if id and id != hotel["id"]:
            continue
        if title and title != hotel["title"]:
            continue
        hotels_.append(hotel)

    return hotels_[(pagination.page - 1) * pagination.per_page:][:pagination.per_page]



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
def create_hotel(
    hotel_data: Hotel = Body(
        openapi_examples={
            "1": {"summary": "Сочи", "value": {"title": "Отель Сочи у моря", "name": "sochi_sea"}},
            "2": {"summary": "Дубай", "value": {"title": "Отель Дубай у фонтана", "name": "dubai_fountain"}}
        }
    )
):
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