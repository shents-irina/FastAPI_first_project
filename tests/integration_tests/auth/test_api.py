import pytest


@pytest.mark.parametrize("email, password, status_code", [
    ("kot1@pes.com", "1234", 200),
    ("kot1@pes.com", "1234", 409),
    ("kot2@pes.com", "12345", 200),
    ("abcde", "1234", 422),
    ("abcde@abc", "1234", 422),
])
async def test_auth_flow(email: str, password: str, status_code: int, ac):
    # /register
    register_response = await ac.post(
        url="/auth/register",
        json={
            "email": email,
            "password": password
        }
    )
    assert register_response.status_code == status_code
    if status_code != 200:
        return

    # /login
    login_response = await ac.post(
        url="/auth/login",
        json={
            "email": email,
            "password": password
        }
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert ac.cookies["access_token"]

    # /me
    user_response = await ac.get(url="/auth/me")
    assert user_response.status_code == 200
    user = user_response.json()
    assert user["email"] == email
    assert "id" in user
    assert "password" not in user
    assert "hashed_password" not in user

    # /logout
    logout_response = await ac.post(url="/auth/logout")
    assert logout_response.status_code == 200
    assert "access_token" not in ac.cookies
