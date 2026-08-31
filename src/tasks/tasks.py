import asyncio
import os

from PIL import Image

from database import async_session_maker_null_pool
from tasks.celery_app import celery_instance
from utils.db_manager import DBManager
from utils.email_manager import EmailManager


@celery_instance.task
def resize_image(image_path: str):
    sizes = [1000, 500, 200]
    output_folder = "src/static/images"

    # Открываем изображение
    img = Image.open(image_path)

    # Получаем имя файла и его расширение
    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)

    # Проходим по каждому размеру
    for size in sizes:
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

    print(f"Изображение сохранено в следующих размерах: {sizes} в папке {output_folder}")


async def get_bookings_with_today_checkin_helper():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        bookings = await db.bookings.get_bookings_with_today_checkin()

        if not bookings:
            return

        with EmailManager() as email_manager:
            for booking in bookings:
                email_manager.send_checkin_reminder_email(
                    email_to=booking.user.email,
                    hotel_title=booking.room.hotel.title,
                    room_title=booking.room.title,
                    date_from=booking.date_from,
                    date_to=booking.date_to,
                )


@celery_instance.task(name="booking_today_checkin")
def send_emails_to_users_with_today_checkin():
    asyncio.run(get_bookings_with_today_checkin_helper())
