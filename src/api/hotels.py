from typing import Annotated

from fastapi import APIRouter, Body, Query
from sqlalchemy import func, insert, select

from src.api.dependencies import PaginationDep
from src.database import async_session_maker, engine
from src.models.hotels import HotelsORM
from src.schemas.hotels import Hotel, HotelPatch

router = APIRouter(prefix='/hotels', tags=['Отели'])


@router.get(path="", summary="Получение данных отеля")
async def get_hotels(
    pagination: PaginationDep,
    # id: int | None = Query(default=None, description="айдишник"),
    title: str | None = Query(default=None, description="название отеля"),
    location: str | None = Query(default=None, description="местоположение отеля"),
):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        query = select(HotelsORM)
        if location:
            query = query.filter(func.lower(HotelsORM.location).contains(location.strip().lower()))
        if title:
            query = query.filter(func.lower(HotelsORM.title).contains(title.strip().lower()))
        query = (
            query
            .offset((pagination.page - 1) * per_page)
            .limit(per_page)
        )
        print(query.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        result =await session.execute(query)

        hotels = result.scalars().all()
        return hotels

    # if pagination.page and pagination.per_page:
    #     return hotels_[(pagination.page - 1) * pagination.per_page:][:pagination.per_page]


# @router.delete(path="/{hotel_id}", summary="Удаление данных отеля")
# def delete_hotels(hotel_id: int):
#     global hotels
#     hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
#     return {"status": "OK"}


@router.post(
    path= "",
    summary="Регистрирует новый отель",
    description="Довавляет данные нового отеля",
)
async def create_hotel(
    hotel_data: Hotel = Body(
        openapi_examples={
            "1": {"summary": "Сочи", "value": {"title": "Отель у моря", "location": "г. Сочи, ул. Морская, 1"}},
            "2": {"summary": "Дубай", "value": {"title": "Отель у фонтана", "location": "г. Дубай, ул. Шейха, 2"}}
        }
    )
):
    async with async_session_maker() as session:
        add_hotel_stmt = insert(HotelsORM).values(**hotel_data.model_dump())
        print(add_hotel_stmt.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        await session.execute(add_hotel_stmt)
        await session.commit()

    return {"status": "OK"}


# @router.put(
#     path="/{hotel_id}",
#     summary="Замена данных отеля",
#     description="Полная замена всех данных",
# )
# def edit_hotel(
#     hotel_id: int,
#     hotel_data: Hotel
# ):
#     global hotels
#     hotel = next(hotel for hotel in hotels if hotel["id"] == hotel_id)
#     hotel["title"] = hotel_data.title
#     hotel["name"] = hotel_data.name
#     return {"status": "OK"}


# @router.patch(
#     path="/{hotel_id}",
#     summary="Частичная замена данных отеля",
#     description="Заменяем какие-то конкретные данные",
# )
# def partial_edit(
#     hotel_id: int,
#     hotel_data: HotelPatch
# ):
#     global hotels
#     hotel = next(hotel for hotel in hotels if hotel["id"] == hotel_id)
#     if hotel_data.title:
#         hotel["title"] = hotel_data.title
#     if hotel_data.name:
#         hotel["name"] = hotel_data.name
#     return {"status": "OK"}