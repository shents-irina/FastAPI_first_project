from fastapi import APIRouter, Body, Query

from api.dependencies import PaginationDep
from database import async_session_maker
from repositories.hotels import HotelsRepository
from schemas.hotels import Hotel, HotelAdd, HotelPatch

router = APIRouter(prefix='/hotels', tags=['Отели'])


@router.get(path="", summary="Получение данных отеля")
async def get_hotels(
    pagination: PaginationDep,
    title: str | None = Query(default=None, description="Название отеля"),
    location: str | None = Query(default=None, description="Местоположение отеля"),
):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_all(
            title,
            location,
            offset=(pagination.page - 1) * per_page,
            limit=per_page
        )


@router.get(
        path="/{hotel_id}",
        summary="Получение данных одного отеля",
        description="Получение одного отеля по id",
    )
async def get_hotel(hotel_id: int):
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_one_or_none(id=hotel_id)


@router.post(
    path= "",
    summary="Регистрирует новый отель",
    description="Довавляет данные нового отеля",
)
async def create_hotel(
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {"summary": "Сочи", "value": {"title": "Отель у моря", "location": "г. Сочи, ул. Морская, 1"}},
            "2": {"summary": "Дубай", "value": {"title": "Отель у фонтана", "location": "г. Дубай, ул. Шейха, 2"}}
        }
    )
):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).add(hotel_data)
        await session.commit()
    return {"status": "OK", "data": hotel}


@router.put(
    path="/{hotel_id}",
    summary="Замена данных отеля",
    description="Полная замена всех данных",
)
async def edit_hotel(
    hotel_id: int,
    hotel_data: HotelAdd
):
    async with async_session_maker() as session:
        await HotelsRepository(session).edit(hotel_data, id=hotel_id)
        await session.commit()
    return {"status": "OK"}


@router.patch(
    path="/{hotel_id}",
    summary="Частичная замена данных отеля",
    description="Заменяем какие-то конкретные данные",
)
async def partial_edit(
    hotel_id: int,
    hotel_data: HotelPatch
):
    async with async_session_maker() as session:
        await HotelsRepository(session).edit(hotel_data, exclude_unset=True, id=hotel_id)
        await session.commit()
    return {"status": "OK"}


@router.delete(path="/{hotel_id}", summary="Удаление данных отеля")
async def delete_hotels(hotel_id: int):
    async with async_session_maker() as session:
        await HotelsRepository(session).delete(id=hotel_id)
        await session.commit()
    return {"status": "OK!"}
