import time

import jwt
import pytest

from config import settings
from exceptions import ExpiredTokenException, IncorrectTokenException
from services.auth import AuthService


def test_create_access_token():
    data = {"user_id": 1}
    jwt_token = AuthService.create_access_token(data)

    assert jwt_token
    assert isinstance(jwt_token, str)


def test_decode_token_returns_original_payload():
    data = {"user_id": 1}
    jwt_token = AuthService.create_access_token(data)

    payload = AuthService.decode_token(jwt_token)

    assert payload
    assert payload["user_id"] == data["user_id"]


def test_decode_token_raises_for_incorrect_token():
    with pytest.raises(IncorrectTokenException):
        AuthService.decode_token("это точно не jwt-токен")


def test_decode_token_raises_for_expired_token():
    expired_payload = {"user_id": 1, "exp": int(time.time()) - 60}
    expired_token = jwt.encode(
        expired_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    with pytest.raises(ExpiredTokenException):
        AuthService.decode_token(expired_token)


def test_hash_password_does_not_contain_plain_text():
    hashed = AuthService.hash_password("super-secret-password")

    assert hashed != "super-secret-password"
    assert isinstance(hashed, str)


def test_verify_password_success_and_failure():
    hashed = AuthService.hash_password("super-secret-password")

    assert AuthService.verify_password("super-secret-password", hashed) is True
    assert AuthService.verify_password("wrong-password", hashed) is False
