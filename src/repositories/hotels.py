from datetime import date

from sqlalchemy import func, select

from models.hotels import HotelsORM
from models.rooms import RoomsORM
from repositories.base import BaseRepository
from repositories.mappers.mappers import HotelDataMapper
from repositories.utils import rooms_ids_for_booking
from schemas.hotels import Hotel


class HotelsRepository(BaseRepository[HotelsORM, Hotel]):
    """Репозиторий отелей."""

    model = HotelsORM
    mapper = HotelDataMapper

    async def get_filtered_by_time(
        self,
        date_from: date,
        date_to: date,
        title,
        location,
        offset,
        limit,
    ) -> list[Hotel]:
        """Возвращает отели со свободными номерами на указанный период.

        В выборку входят отели, где есть хотя бы один номер, свободный на период от ``date_from`` до ``date_to``.
        Доступность номера определяет ``rooms_ids_for_booking``.

        Фильтры ``title`` и ``location`` ищут подстроку без учёта регистра, пробелы по краям игнорируются.
        Пустое значение или ``None`` отключает фильтр.

        :param date_from: Начало периода.
        :param date_to: Конец периода.
        :param title: Часть названия отеля.
        :param location: Часть адреса или местоположения отеля.
        :param offset: Сколько отелей пропустить с начала выборки.
        :param limit: Максимальное число отелей в результате.
        :return: Список отелей или пустой список, если подходящих нет.
        """
        rooms_ids_to_get = rooms_ids_for_booking(date_from=date_from, date_to=date_to)
        hotels_ids_to_get = (
            select(RoomsORM.hotel_id)
            .select_from(RoomsORM)
            .filter(RoomsORM.id.in_(rooms_ids_to_get))
        )

        query = select(HotelsORM).filter(HotelsORM.id.in_(hotels_ids_to_get))
        if location:
            query = query.filter(func.lower(HotelsORM.location).contains(location.strip().lower()))
        if title:
            query = query.filter(func.lower(HotelsORM.title).contains(title.strip().lower()))
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)

        return [self.mapper.map_to_domain_entity(hotel) for hotel in result.scalars().all()]
