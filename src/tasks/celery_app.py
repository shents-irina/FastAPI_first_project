from celery import Celery
from celery.schedules import crontab

from config import settings

celery_instance = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    include=[
        "tasks.tasks",
    ],
)

# Расписание Celery beat: ежедневная рассылка напоминаний о заезде в 01:00 по UTC
celery_instance.conf.beat_schedule = {
    "Напоминание о заезде": {
        "task": "booking_today_checkin",
        "schedule": crontab(hour=1, minute=0),
    }
}
