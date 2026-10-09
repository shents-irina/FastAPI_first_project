import uuid
from datetime import UTC, datetime, timedelta

import pytest

from schemas.bookings import BookingAdd
from schemas.hotels import HotelAdd
from schemas.rooms import RoomAdd


def today():
    return datetime.now(tz=UTC).date()


@pytest.fixture
async def hotel_id(db):
    hotel = await db.hotels.add(
        HotelAdd(
            title=f"Отель для тестов номеров{uuid.uuid4()}", location="г. Тест, ул. Номерная, 1"
        )
    )
    await db.commit()
    return hotel.id


async def test_create_room(ac, hotel_id):
    response = await ac.post(
        f"/hotels/{hotel_id}/rooms",
        json={
            "title": "Стандарт",
            "description": "Обычный номер",
            "price": 3000,
            "quantity": 3,
            "facilities_ids": [],
        },
    )
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "OK"
    assert res["data"]["title"] == "Стандарт"
    assert res["data"]["hotel_id"] == hotel_id


async def test_create_room_for_nonexistent_hotel_returns_404(ac):
    response = await ac.post(
        "/hotels/999999/rooms", json={"title": "Стандарт", "price": 1000, "quantity": 1}
    )
    assert response.status_code == 404


async def test_create_duplicate_room_returns_409(ac, hotel_id):
    payload = {"title": "Люкс", "price": 5000, "quantity": 2}

    first_response = await ac.post(f"/hotels/{hotel_id}/rooms", json=payload)
    assert first_response.status_code == 200

    second_response = await ac.post(f"/hotels/{hotel_id}/rooms", json=payload)
    assert second_response.status_code == 409


async def test_create_room_with_unknown_facility_returns_404(ac, hotel_id):
    response = await ac.post(
        f"/hotels/{hotel_id}/rooms",
        json={
            "title": "Номер с удобствами",
            "price": 1000,
            "quantity": 1,
            "facilities_ids": [999999],
        },
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    "field, bad_value",
    [
        ("price", -100),
        ("quantity", -1),
    ],
)
async def test_create_room_with_negative_values_returns_422(ac, hotel_id, field, bad_value):
    payload = {"title": "Плохой номер", "price": 1000, "quantity": 1, field: bad_value}
    response = await ac.post(f"/hotels/{hotel_id}/rooms", json=payload)
    assert response.status_code == 422


async def test_get_room_not_found_returns_404(ac, hotel_id):
    response = await ac.get(f"/hotels/{hotel_id}/rooms/999999")
    assert response.status_code == 404


async def test_get_rooms_for_nonexistent_hotel_returns_404(ac):
    date_from = (today() + timedelta(days=1)).isoformat()
    date_to = (today() + timedelta(days=5)).isoformat()
    response = await ac.get(
        "/hotels/999999/rooms", params={"date_from": date_from, "date_to": date_to}
    )
    assert response.status_code == 404


async def test_get_rooms_checkout_before_checkin_returns_422(ac, hotel_id):
    date_from = (today() + timedelta(days=5)).isoformat()
    date_to = (today() + timedelta(days=1)).isoformat()
    response = await ac.get(
        f"/hotels/{hotel_id}/rooms", params={"date_from": date_from, "date_to": date_to}
    )
    assert response.status_code == 422


async def test_get_rooms_returns_created_room(ac, hotel_id):
    create_response = await ac.post(
        f"/hotels/{hotel_id}/rooms",
        json={"title": "Созданный номер", "price": 1500, "quantity": 2},
    )
    assert create_response.status_code == 200
    room_id = create_response.json()["data"]["id"]

    date_from = (today() + timedelta(days=1)).isoformat()
    date_to = (today() + timedelta(days=5)).isoformat()
    response = await ac.get(
        f"/hotels/{hotel_id}/rooms", params={"date_from": date_from, "date_to": date_to}
    )
    assert response.status_code == 200
    room_ids = [room["id"] for room in response.json()]
    assert room_id in room_ids


async def test_room_crud_flow(ac, hotel_id):
    create_response = await ac.post(
        f"/hotels/{hotel_id}/rooms",
        json={"title": "CRUD номер", "price": 2000, "quantity": 5, "facilities_ids": []},
    )
    assert create_response.status_code == 200
    room_id = create_response.json()["data"]["id"]

    get_response = await ac.get(f"/hotels/{hotel_id}/rooms/{room_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "CRUD номер"
    assert get_response.json()["facilities"] == []

    put_response = await ac.put(
        f"/hotels/{hotel_id}/rooms/{room_id}",
        json={
            "title": "CRUD номер (обновлён)",
            "price": 2500,
            "quantity": 4,
            "facilities_ids": [],
        },
    )
    assert put_response.status_code == 200

    patch_response = await ac.patch(f"/hotels/{hotel_id}/rooms/{room_id}", json={"price": 2700})
    assert patch_response.status_code == 200

    get_after_patch = await ac.get(f"/hotels/{hotel_id}/rooms/{room_id}")
    room = get_after_patch.json()
    assert room["price"] == 2700
    assert room["title"] == "CRUD номер (обновлён)"

    delete_response = await ac.delete(f"/hotels/{hotel_id}/rooms/{room_id}")
    assert delete_response.status_code == 200

    get_after_delete = await ac.get(f"/hotels/{hotel_id}/rooms/{room_id}")
    assert get_after_delete.status_code == 404


async def test_edit_nonexistent_room_returns_404(ac, hotel_id):
    response = await ac.put(
        f"/hotels/{hotel_id}/rooms/999999",
        json={"title": "Не существует", "price": 100, "quantity": 1},
    )
    assert response.status_code == 404


async def test_partial_edit_nonexistent_room_returns_404(ac, hotel_id):
    response = await ac.patch(f"/hotels/{hotel_id}/rooms/999999", json={"price": 100})
    assert response.status_code == 404


async def test_delete_nonexistent_room_returns_404(ac, hotel_id):
    response = await ac.delete(f"/hotels/{hotel_id}/rooms/999999")
    assert response.status_code == 404


async def test_edit_room_to_duplicate_title_returns_409(ac, hotel_id):
    first_payload = {"title": "Стандарт А", "price": 1000, "quantity": 1}
    second_payload = {"title": "Стандарт Б", "price": 1000, "quantity": 1}

    await ac.post(f"/hotels/{hotel_id}/rooms", json=first_payload)
    second_response = await ac.post(f"/hotels/{hotel_id}/rooms", json=second_payload)
    second_room_id = second_response.json()["data"]["id"]

    put_response = await ac.put(
        f"/hotels/{hotel_id}/rooms/{second_room_id}",
        json=first_payload,
    )
    assert put_response.status_code == 409


async def test_delete_room_with_active_booking_returns_409(ac, db, hotel_id):
    room = await db.rooms.add(
        RoomAdd(hotel_id=hotel_id, title="Забронированный номер", price=100, quantity=1)
    )
    user_id = (await db.users.get_all())[0].id
    await db.bookings.add(
        BookingAdd(
            user_id=user_id,
            room_id=room.id,
            date_from=today() + timedelta(days=110),
            date_to=today() + timedelta(days=115),
            price=100,
        )
    )
    await db.commit()

    response = await ac.delete(f"/hotels/{hotel_id}/rooms/{room.id}")
    assert response.status_code == 409
