import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from schemas.hotels import HotelAdd
from schemas.rooms import RoomAdd
from tests.conftest import get_db_null_pool

BASE_OFFSET = 30


def today():
    return datetime.now(tz=UTC).date()


def future_date(days_offset: int) -> str:
    return (today() + timedelta(days=days_offset)).isoformat()


@pytest.fixture(scope="module")
async def delete_all_bookings():
    async for _db in get_db_null_pool():
        await _db.bookings.delete()
        await _db.commit()


@pytest.fixture
async def booking_room(db):
    unique_suffix = uuid.uuid4().hex
    hotel = await db.hotels.add(
        HotelAdd(title=f"Отель для брони {unique_suffix}", location="Тестовый адрес")
    )
    room = await db.rooms.add(
        RoomAdd(hotel_id=hotel.id, title=f"Номер для брони {unique_suffix}", price=1000, quantity=1)
    )
    await db.commit()
    return room


@pytest.fixture
async def other_authenticated_ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        email = "other_user@pes.com"
        await client.post(url="/auth/register", json={"email": email, "password": "1234"})
        await client.post(url="/auth/login", json={"email": email, "password": "1234"})
        yield client


@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_code",
    [
        (1, future_date(BASE_OFFSET + 0), future_date(BASE_OFFSET + 4), 200),
        (1, future_date(BASE_OFFSET + 1), future_date(BASE_OFFSET + 4), 200),
        (1, future_date(BASE_OFFSET + 0), future_date(BASE_OFFSET + 3), 200),
        (1, future_date(BASE_OFFSET + 0), future_date(BASE_OFFSET + 2), 200),
        (1, future_date(BASE_OFFSET + 0), future_date(BASE_OFFSET + 5), 200),
        (1, future_date(BASE_OFFSET + 2), future_date(BASE_OFFSET + 4), 409),
        (1, future_date(BASE_OFFSET + 4), future_date(BASE_OFFSET + 9), 200),
    ],
)
async def test_add_booking(db, authenticated_ac, room_id, date_from, date_to, status_code):
    response = await authenticated_ac.post(
        url="/bookings", json={"room_id": room_id, "date_from": date_from, "date_to": date_to}
    )
    assert response.status_code == status_code
    if status_code == 200:
        res = response.json()
        assert isinstance(res, dict)
        assert res["status"] == "OK"
        assert "data" in res


@pytest.mark.parametrize(
    "room_id, date_from, date_to, quantity_bookings",
    [
        (1, future_date(BASE_OFFSET + 0), future_date(BASE_OFFSET + 4), 1),
        (1, future_date(BASE_OFFSET + 0), future_date(BASE_OFFSET + 4), 2),
        (1, future_date(BASE_OFFSET + 0), future_date(BASE_OFFSET + 4), 3),
    ],
)
async def test_add_and_get_bookings(
    room_id,
    date_from,
    date_to,
    quantity_bookings,
    delete_all_bookings,
    authenticated_ac,
):
    response = await authenticated_ac.post(
        url="/bookings", json={"room_id": room_id, "date_from": date_from, "date_to": date_to}
    )
    assert response.status_code == 200

    response_my_bookings = await authenticated_ac.get(url="/bookings/me")
    assert response_my_bookings.status_code == 200
    assert len(response_my_bookings.json()) == quantity_bookings


async def test_add_booking_requires_authentication_returns_401(ac, booking_room):
    response = await ac.post(
        url="/bookings",
        json={
            "room_id": booking_room.id,
            "date_from": future_date(BASE_OFFSET + 60),
            "date_to": future_date(BASE_OFFSET + 64),
        },
    )
    assert response.status_code == 401


async def test_get_my_bookings_requires_authentication_returns_401(ac):
    response = await ac.get(url="/bookings/me")
    assert response.status_code == 401


async def test_add_booking_for_nonexistent_room_returns_404(authenticated_ac):
    response = await authenticated_ac.post(
        url="/bookings",
        json={
            "room_id": 999999,
            "date_from": future_date(BASE_OFFSET + 60),
            "date_to": future_date(BASE_OFFSET + 64),
        },
    )
    assert response.status_code == 404


async def test_add_booking_checkout_before_checkin_returns_422(authenticated_ac, booking_room):
    response = await authenticated_ac.post(
        url="/bookings",
        json={
            "room_id": booking_room.id,
            "date_from": future_date(BASE_OFFSET + 64),
            "date_to": future_date(BASE_OFFSET + 60),
        },
    )
    assert response.status_code == 422


async def test_add_booking_in_the_past_returns_422(authenticated_ac, booking_room):
    yesterday = (today() - timedelta(days=1)).isoformat()
    response = await authenticated_ac.post(
        url="/bookings",
        json={"room_id": booking_room.id, "date_from": yesterday, "date_to": future_date(0)},
    )
    assert response.status_code == 422


async def test_add_booking_no_rooms_left_returns_409(authenticated_ac, booking_room):
    payload = {
        "room_id": booking_room.id,
        "date_from": future_date(BASE_OFFSET + 70),
        "date_to": future_date(BASE_OFFSET + 74),
    }
    first_response = await authenticated_ac.post(url="/bookings", json=payload)
    assert first_response.status_code == 200

    second_response = await authenticated_ac.post(url="/bookings", json=payload)
    assert second_response.status_code == 409


async def test_users_see_only_their_own_bookings(
    authenticated_ac, other_authenticated_ac, booking_room, db
):
    hotel = await db.hotels.add(
        HotelAdd(title="Отель для второго пользователя", location="ул. Вторая, 1")
    )
    other_room = await db.rooms.add(
        RoomAdd(hotel_id=hotel.id, title="Номер для второго пользователя", price=500, quantity=1)
    )
    await db.commit()

    await authenticated_ac.post(
        url="/bookings",
        json={
            "room_id": booking_room.id,
            "date_from": future_date(BASE_OFFSET + 80),
            "date_to": future_date(BASE_OFFSET + 84),
        },
    )
    await other_authenticated_ac.post(
        url="/bookings",
        json={
            "room_id": other_room.id,
            "date_from": future_date(BASE_OFFSET + 80),
            "date_to": future_date(BASE_OFFSET + 84),
        },
    )

    my_bookings = (await authenticated_ac.get(url="/bookings/me")).json()
    other_bookings = (await other_authenticated_ac.get(url="/bookings/me")).json()

    my_room_ids = {b["room_id"] for b in my_bookings}
    other_room_ids = {b["room_id"] for b in other_bookings}

    assert booking_room.id in my_room_ids
    assert other_room.id not in my_room_ids
    assert other_room.id in other_room_ids
    assert booking_room.id not in other_room_ids


async def test_delete_booking(authenticated_ac, booking_room):
    create_response = await authenticated_ac.post(
        url="/bookings",
        json={
            "room_id": booking_room.id,
            "date_from": future_date(BASE_OFFSET + 90),
            "date_to": future_date(BASE_OFFSET + 94),
        },
    )
    booking_id = create_response.json()["data"]["id"]

    delete_response = await authenticated_ac.delete(f"/bookings/{booking_id}")
    assert delete_response.status_code == 200

    my_bookings = (await authenticated_ac.get(url="/bookings/me")).json()
    assert booking_id not in {b["id"] for b in my_bookings}


async def test_delete_nonexistent_booking_returns_404(authenticated_ac):
    response = await authenticated_ac.delete("/bookings/999999")
    assert response.status_code == 404


async def test_cannot_delete_booking_that_already_started_returns_409(
    authenticated_ac, booking_room
):
    create_response = await authenticated_ac.post(
        url="/bookings",
        json={
            "room_id": booking_room.id,
            "date_from": today().isoformat(),
            "date_to": future_date(4),
        },
    )
    assert create_response.status_code == 200
    booking_id = create_response.json()["data"]["id"]

    response = await authenticated_ac.delete(f"/bookings/{booking_id}")
    assert response.status_code == 409


async def test_cannot_delete_other_users_booking(
    authenticated_ac, other_authenticated_ac, booking_room
):
    create_response = await authenticated_ac.post(
        url="/bookings",
        json={
            "room_id": booking_room.id,
            "date_from": future_date(BASE_OFFSET + 100),
            "date_to": future_date(BASE_OFFSET + 104),
        },
    )
    booking_id = create_response.json()["data"]["id"]

    response = await other_authenticated_ac.delete(f"/bookings/{booking_id}")
    assert response.status_code == 404

    own_delete_response = await authenticated_ac.delete(f"/bookings/{booking_id}")
    assert own_delete_response.status_code == 200
