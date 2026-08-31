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

celery_instance.conf.beat_schedule = {
    "Напоминание о заезде": {
        "task": "booking_today_checkin",
        "schedule": crontab(hour=8, minute=0),
    }
}
