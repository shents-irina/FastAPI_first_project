from io import BytesIO
from unittest import mock

from fastapi import UploadFile

from services.images import ImageService


def test_upload_image_saves_file_and_schedules_resize():
    upload_file = UploadFile(file=BytesIO(b"fake-image-bytes"), filename="photo.jpg")

    with (
        mock.patch("builtins.open", mock.mock_open()) as mock_file_open,
        mock.patch("services.images.shutil.copyfileobj") as mock_copy,
        mock.patch("services.images.resize_image") as mock_resize_image,
    ):
        ImageService.upload_image(upload_file)

    mock_file_open.assert_called_once_with("src/static/images/photo.jpg", "wb+")
    mock_copy.assert_called_once()
    mock_resize_image.delay.assert_called_once_with("src/static/images/photo.jpg")
