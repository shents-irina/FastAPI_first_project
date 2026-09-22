import shutil

from fastapi import UploadFile

from tasks.tasks import resize_image


class ImageService:
    @staticmethod
    def upload_image(file: UploadFile):
        image_path = f"src/static/images/{file.filename}"
        with open(image_path, "wb+") as new_file:
            shutil.copyfileobj(file.file, new_file)

        resize_image.delay(image_path)  # pyright: ignore[reportFunctionMemberAccess]  # celery добавляет .delay в рантайме
