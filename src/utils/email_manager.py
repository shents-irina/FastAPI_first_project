import logging
import smtplib
from datetime import date
from email.message import EmailMessage
from typing import Self

from config import settings

logger = logging.getLogger(__name__)


class EmailManager:
    """Отправка писем через SMTP. Используется как контекстный менеджер.

    Открывает защищённое SMTP-соединение при входе в ``with`` и закрывает его при выходе.
    Одно соединение можно использовать для нескольких писем.

    Пример:
        with EmailManager() as email_manager:
            email_manager.send_email("user@example.com", "Тема", "Текст")
    """

    def __enter__(self) -> Self:
        """Подключается к SMTP-серверу и входит в учётную запись.

        Параметры подключения берутся из ``settings``.

        :return: Сам менеджер.
        """
        logger.debug("Подключаюсь к SMTP host=%s, port=%s", settings.SMTP_HOST, settings.SMTP_PORT)
        self._server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        try:
            self._server.login(settings.SMTP_USER, settings.SMTP_PASS)
        except Exception:
            logger.error("Ошибка при входе на SMTP-сервер host=%s, port=%s", settings.SMTP_HOST, settings.SMTP_PORT)
            self._server.close()
            raise
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Завершает SMTP-сессию."""
        self._server.quit()

    def send_email(self, email_to: str, subject: str, text_content: str) -> None:
        """Отправляет простое текстовое письмо от имени ``settings.SMTP_USER``.

        :param email_to: Адрес получателя.
        :param subject: Тема письма.
        :param text_content: Текст письма (обычный текст, не HTML).
        :raises smtplib.SMTPException: SMTP-сервер отклонил письмо или соединение потеряно.
        """
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings.SMTP_USER
        message["To"] = email_to
        message.set_content(text_content)

        self._server.send_message(message)
        logger.info("Письмо отправлено, subject=%r", subject)

    def send_checkin_reminder_email(
        self,
        email_to: str,
        hotel_title: str,
        room_title: str,
        date_from: date,
        date_to: date,
    ) -> None:
        """Отправляет гостю напоминание о том, что сегодня у него заезд.

        В письме указываются отель, номер и даты заезда и выезда.

        :param email_to: Адрес гостя.
        :param hotel_title: Название отеля.
        :param room_title: Название номера.
        :param date_from: Дата заезда.
        :param date_to: Дата выезда.
        """
        text_content = (
            "Здравствуйте!\n\n"
            "Напоминаем, что сегодня у вас запланирован заезд.\n\n"
            f"Отель: {hotel_title}\n"
            f"Номер: {room_title}\n"
            f"Дата заезда: {date_from}\n"
            f"Дата выезда: {date_to}\n\n"
            "Ждём вас!"
        )

        self.send_email(
            email_to=email_to,
            subject=f"Напоминание: сегодня у вас заезд в {hotel_title}!",
            text_content=text_content,
        )
