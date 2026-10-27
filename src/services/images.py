import logging
import shutil

from fastapi import UploadFile

from tasks.tasks import resize_image

logger = logging.getLogger(__name__)


class ImageService:
    """Сервис изображений: сохранение загруженных файлов, запуск создания уменьшенных копий."""

    @staticmethod
    def upload_image(file: UploadFile) -> None:
        """Сохраняет загруженное изображение и запускает его обработку.

        Файл записывается в ``src/static/images/`` под исходным именем. Если файл с таким именем уже есть, он перезаписывается.
        В очередь Celery ставится фоновая задача ``resize_image``, которая создает уменьшенные копии. Метод не дожидается её завершения.

        :param file: Загруженное изображение.
        """
        image_path = f"src/static/images/{file.filename}"
        with open(image_path, "wb+") as new_file:
            shutil.copyfileobj(file.file, new_file)
        logger.info("Изображение сохранено: %s", image_path)

        resize_image.delay(image_path)  # pyright: ignore[reportFunctionMemberAccess]  # celery добавляет .delay в рантайме
        logger.debug("Задача resize_image поставлена в очередь для %s", image_path)
