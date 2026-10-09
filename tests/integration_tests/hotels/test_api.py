from datetime import UTC, datetime, timedelta

from schemas.bookings import BookingAdd
from schemas.hotels import HotelAdd
from schemas.rooms import RoomAdd


def today():
    return datetime.now(tz=UTC).date()


async def test_get_hotels(ac):
    date_from = (today() + timedelta(days=1)).isoformat()
    date_to = (today() + timedelta(days=5)).isoformat()
    response = await ac.get(url="/hotels", params={"date_from": date_from, "date_to": date_to})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_get_hotels_checkout_before_checkin_returns_422(ac):
    date_from = (today() + timedelta(days=10)).isoformat()
    date_to = (today() + timedelta(days=5)).isoformat()
    response = await ac.get(url="/hotels", params={"date_from": date_from, "date_to": date_to})
    assert response.status_code == 422


async def test_hotels_pagination_splits_results_across_pages(ac, db):
    date_from = (today() + timedelta(days=200)).isoformat()
    date_to = (today() + timedelta(days=205)).isoformat()

    for i in range(3):
        hotel = await db.hotels.add(
            HotelAdd(title=f"Пагинация {i}", location=f"ул. Пагинации, {i}")
        )
        await db.rooms.add(RoomAdd(hotel_id=hotel.id, title=f"Номер {i}", price=1000, quantity=1))
    await db.commit()

    common_params = {"date_from": date_from, "date_to": date_to, "title": "Пагинация"}

    first_page = await ac.get("/hotels", params={**common_params, "per_page": 2, "page": 1})
    assert first_page.status_code == 200
    assert len(first_page.json()) == 2
    first_page_titles = {hotel["title"] for hotel in first_page.json()}
    assert all("Пагинация" in title for title in first_page_titles)

    second_page = await ac.get("/hotels", params={**common_params, "per_page": 2, "page": 2})
    assert second_page.status_code == 200
    assert len(second_page.json()) == 1
    second_page_titles = {hotel["title"] for hotel in second_page.json()}
    assert all("Пагинация" in title for title in second_page_titles)

    assert len(first_page_titles | second_page_titles) == 3
    assert len(first_page_titles & second_page_titles) == 0


async def test_get_hotel_not_found_returns_404(ac):
    response = await ac.get(url="/hotels/999999")
    assert response.status_code == 404


async def test_hotel_crud_flow(ac):
    title = "Тестовый отель CRUD"
    location = "г. Круд, ул. Тестовая"

    create_response = await ac.post("/hotels", json={"title": title, "location": location})
    assert create_response.status_code == 200
    hotel = create_response.json()["data"]
    hotel_id = hotel["id"]
    assert hotel["title"] == title

    get_response = await ac.get(f"/hotels/{hotel_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == title

    new_title = f"{title} (обновлён)"
    new_location = f"{location}, дом 2"
    put_response = await ac.put(
        f"/hotels/{hotel_id}", json={"title": new_title, "location": new_location}
    )
    assert put_response.status_code == 200

    patched_title = f"{title} (частично обновлён)"
    patch_response = await ac.patch(f"/hotels/{hotel_id}", json={"title": patched_title})
    assert patch_response.status_code == 200

    get_after_patch = await ac.get(f"/hotels/{hotel_id}")
    hotel = get_after_patch.json()
    assert hotel["title"] == patched_title
    assert hotel["location"] == new_location

    delete_response = await ac.delete(f"/hotels/{hotel_id}")
    assert delete_response.status_code == 200

    get_after_delete = await ac.get(f"/hotels/{hotel_id}")
    assert get_after_delete.status_code == 404


async def test_edit_nonexistent_hotel_returns_404(ac):
    response = await ac.put("/hotels/999999", json={"title": "Не существует", "location": "Нигде"})
    assert response.status_code == 404


async def test_delete_nonexistent_hotel_returns_404(ac):
    response = await ac.delete("/hotels/999999")
    assert response.status_code == 404


async def test_create_duplicate_hotel_returns_409(ac):
    payload = {"title": "Дубликат отеля", "location": "г. Дубликат, ул. Первая, 1"}

    first_response = await ac.post("/hotels", json=payload)
    assert first_response.status_code == 200

    second_response = await ac.post("/hotels", json=payload)
    assert second_response.status_code == 409


async def test_edit_hotel_to_duplicate_returns_409(ac):
    first_payload = {"title": "Первый отель", "location": "г. Первый, ул. А, 1"}
    second_payload = {"title": "Второй отель", "location": "г. Второй, ул. Б, 2"}

    await ac.post("/hotels", json=first_payload)
    second_response = await ac.post("/hotels", json=second_payload)
    second_hotel_id = second_response.json()["data"]["id"]

    # Пытаемся переименовать второй отель точно как первый.
    response = await ac.put(f"/hotels/{second_hotel_id}", json=first_payload)
    assert response.status_code == 409


async def test_delete_hotel_with_booked_room_returns_409(db, ac):
    hotel = await db.hotels.add(
        HotelAdd(title="Отель с бронью", location="г. Тест, ул. Занятая, 1")
    )
    room = await db.rooms.add(
        RoomAdd(hotel_id=hotel.id, title="Забронированный номер", price=100, quantity=1)
    )
    user_id = (await db.users.get_all())[0].id
    await db.bookings.add(
        BookingAdd(
            user_id=user_id,
            room_id=room.id,
            date_from=today() + timedelta(days=100),
            date_to=today() + timedelta(days=105),
            price=100,
        )
    )
    await db.commit()

    response = await ac.delete(f"/hotels/{hotel.id}")
    assert response.status_code == 409
