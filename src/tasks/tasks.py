import asyncio
import logging
import os
import smtplib

from PIL import Image

from database import async_session_maker_null_pool
from tasks.celery_app import celery_instance
from utils.db_manager import DBManager
from utils.email_manager import EmailManager

logger = logging.getLogger(__name__)


@celery_instance.task
def resize_image(image_path: str):
    """Создаёт уменьшенные копии изображения.

    Для каждой ширины из ``[1000, 500, 200]`` пикселей сохраняет копию с сохранением пропорций в ``src/static/images``
    под именем ``<имя>_<ширина>px<расширение>``. Исходный файл не изменяется.
    Если исходное изображение уже меньше нужной ширины, копия не будет увеличена.

    :param image_path: Путь к уже сохранённому на диск оригиналу изображения.
    """
    logger.debug("Вызывается функция resize_image с image_path=%s", image_path)
    sizes = [1000, 500, 200]
    output_folder = "src/static/images"

    # Получаем имя файла и его расширение
    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)

    with Image.open(image_path) as img:
        # Проходим по каждому размеру
        for size in sizes:
            # Увеличивать картинку незачем: качество ухудшится
            if size > img.width:
                logger.debug("Пропускаю размер %s: исходная ширина %s", size, img.width)
                continue

            # Сжимаем изображение
            image_resized = img.resize(
                (size, int(img.height * (size / img.width))), Image.Resampling.LANCZOS
            )
            # Формируем имя нового файла
            new_file_name = f"{name}_{size}px{ext}"
            # Полный путь для сохранения
            output_path = os.path.join(output_folder, new_file_name)
            # Сохраняем изображение
            image_resized.save(output_path)

    logger.info("Изображение сохранено в следующих размерах: %s в папке %s", sizes, output_folder)


async def get_bookings_with_today_checkin_helper():
    """Отправляет напоминания пользователям, у которых заезд сегодня.

    Находит бронирования с заездом на текущую дату и для каждого отправляет письмо владельцу брони.
    Если таких бронирований нет, ничего не делает.
    """
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        bookings = await db.bookings.get_bookings_with_today_checkin()

        if not bookings:
            logger.info("Сегодня нет заездов, напоминания не нужны")
            return

        logger.info("Заездов сегодня: %s, отправляю напоминания", len(bookings))
        failed = 0
        with EmailManager() as email_manager:
            for booking in bookings:
                try:
                    email_manager.send_checkin_reminder_email(
                        email_to=booking.user.email,
                        hotel_title=booking.room.hotel.title,
                        room_title=booking.room.title,
                        date_from=booking.date_from,
                        date_to=booking.date_to,
                    )
                except smtplib.SMTPException:
                    failed += 1
                    logger.exception("Не удалось отправить напоминание booking_id=%s", booking.id)
        logger.info(
            "Напоминания о заезде: отправлено %s, с ошибкой %s", len(bookings) - failed, failed
        )


@celery_instance.task(name="booking_today_checkin")
def send_emails_to_users_with_today_checkin():
    """Задача Celery: рассылка напоминаний о заезде.

    Запускает асинхронную рассылку ``get_bookings_with_today_checkin_helper`` и дожидается её завершения.
    Выполняется по расписанию Celery beat.
    """
    logger.info("Запущена задача рассылки напоминаний о заезде")
    asyncio.run(get_bookings_with_today_checkin_helper())
