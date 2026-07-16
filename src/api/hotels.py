from datetime import date

from fastapi import APIRouter, Body, Query

from api.dependencies import DBDep, PaginationDep
from schemas.hotels import HotelAdd, HotelPatch


router = APIRouter(prefix='/hotels', tags=['Отели'])


@router.get(path="", summary="Получение данных отеля")
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    date_from: date = Query(openapi_examples={"example1": {"summary": "Пример даты заезда", "value": "2026-07-07"}}),
    date_to: date = Query(openapi_examples={"example1": {"summary": "Пример даты выезда", "value": "2026-08-12"}}),
    title: str | None = Query(default=None, description="Название отеля"),
    location: str | None = Query(default=None, description="Местоположение отеля"),
):
    per_page = pagination.per_page or 5
    return await db.hotels.get_filtered_by_time(
        date_from=date_from,
        date_to=date_to,
        title=title,
        location=location,
        offset=(pagination.page - 1) * per_page,
        limit=per_page,
    )


@router.get(
        path="/{hotel_id}",
        summary="Получение данных одного отеля",
        description="Получение одного отеля по id",
    )
async def get_hotel(
    db: DBDep,
    hotel_id: int
):
    return await db.hotels.get_one_or_none(id=hotel_id)


@router.post(
    path= "",
    summary="Регистрирует новый отель",
    description="Добавляет данные нового отеля",
)
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {"summary": "Сочи", "value": {"title": "Отель у моря", "location": "г. Сочи, ул. Морская, 1"}},
            "2": {"summary": "Дубай", "value": {"title": "Отель у фонтана", "location": "г. Дубай, ул. Шейха, 2"}}
        }
    )
):
    hotel = await db.hotels.add(hotel_data)
    await db.commit()
    return {"status": "OK", "data": hotel}


@router.put(
    path="/{hotel_id}",
    summary="Замена данных отеля",
    description="Полная замена всех данных",
)
async def edit_hotel(
    db: DBDep,
    hotel_id: int,
    hotel_data: HotelAdd
):
    await db.hotels.edit(hotel_data, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.patch(
    path="/{hotel_id}",
    summary="Частичная замена данных отеля",
    description="Заменяем какие-то конкретные данные",
)
async def partial_edit(
    db: DBDep,
    hotel_id: int,
    hotel_data: HotelPatch
):
    await db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.delete(path="/{hotel_id}", summary="Удаление данных отеля")
async def delete_hotels(
    db: DBDep,
    hotel_id: int
):
    await db.hotels.delete(id=hotel_id)
    await db.commit()
    return {"status": "OK!"}
