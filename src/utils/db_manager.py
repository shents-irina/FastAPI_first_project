from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from repositories.bookings import BookingsRepository
from repositories.facilities import FacilitiesRepository, RoomsFacilitiesRepository
from repositories.hotels import HotelsRepository
from repositories.rooms import RoomsRepository
from repositories.users import UsersRepository


class DBManager:
    """Менеджер работы с БД: даёт доступ ко всем репозиториям через одну общую сессию.

    Используется как асинхронный контекстный менеджер.
    На входе создаёт сессию и репозитории, на выходе откатывает незафиксированные изменения и закрывает сессию.
    Изменения попадают в БД только после явного вызова ``commit``.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """Запоминает, чем создавать сессию.

        Сессия откроется позже, когда начнётся блок ``async with DBManager(...)``.

        :param session_factory: Функция, которая при вызове создаёт новую сессию БД.
        """
        self.session_factory = session_factory

    async def __aenter__(self):
        """Открывает сессию и создаёт репозитории, работающие в этой сессии.

        Все репозитории получают одну и ту же сессию, поэтому их операции выполняются в одной транзакции.

        :return: Текущий экземпляр DBManager с доступом к репозиториям.
        """
        self.session = self.session_factory()

        self.users = UsersRepository(self.session)
        self.hotels = HotelsRepository(self.session)
        self.rooms = RoomsRepository(self.session)
        self.bookings = BookingsRepository(self.session)
        self.facilities = FacilitiesRepository(self.session)
        self.rooms_facilities = RoomsFacilitiesRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Откатывает незавершённую транзакцию и закрывает сессию.

        Откат выполняется всегда. Если ``commit`` уже вызван, откатывать нечего.
        Если в блоке возникла ошибка или ``commit`` не вызвали, изменения в БД не попадут.
        Сама ошибка не подавляется и уходит дальше.

        :param exc_type: Тип возникшего исключения или None.
        :param exc: Экземпляр возникшего исключения или None.
        :param tb: Трассировка возникшего исключения или None.
        """
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        """Фиксирует изменения текущей транзакции в базе данных."""
        await self.session.commit()
