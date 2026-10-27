from fastapi import APIRouter, UploadFile

from services.images import ImageService

router = APIRouter(prefix="/images", tags=["Изображения отелей"])


@router.post("")
def upload_image(file: UploadFile):
    """Загружает изображение отеля.

    Оригинал сохраняется на диск, а создание уменьшенных копий передаётся в фоновую задачу Celery.
    """
    ImageService.upload_image(file)
