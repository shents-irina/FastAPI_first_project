import smtplib
from email.message import EmailMessage
from typing import Self

from config import settings


class EmailManager:
    def __enter__(self) -> Self:
        self._server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        self._server.login(settings.SMTP_USER, settings.SMTP_PASS)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._server.quit()

    def send_email(self, email_to: str, subject: str, text_content: str) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings.SMTP_USER
        message["To"] = email_to
        message.set_content(text_content)

        self._server.send_message(message)

    def send_checkin_reminder_email(
        self,
        email_to: str,
        hotel_title: str,
        room_title: str,
        date_from,
        date_to,
    ) -> None:
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
