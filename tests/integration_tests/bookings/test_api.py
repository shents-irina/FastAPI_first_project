import pytest

from database import async_session_maker_null_pool
from tests.conftest import get_db_null_pool
from utils.db_manager import DBManager


@pytest.mark.parametrize("room_id, date_from, date_to, status_code", [
    (1, "2026-08-01", "2026-08-05", 200),
    (1, "2026-08-01", "2026-08-05", 200),
    (1, "2026-08-01", "2026-08-04", 200),
    (1, "2026-08-01", "2026-08-03", 200),
    (1, "2026-08-01", "2026-08-02", 200),
    (1, "2026-08-01", "2026-08-05", 409),
    (1, "2026-08-05", "2026-08-10", 200),
])
async def test_add_booking(db, authenticated_ac, room_id, date_from, date_to, status_code):
    response = await authenticated_ac.post(
        url="/bookings",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to
        }
    )
    assert response.status_code == status_code
    if status_code == 200:
        res = response.json()
        assert isinstance(res, dict)
        assert res["status"] == "OK"
        assert "data" in res


@pytest.fixture(scope="module")
async def delete_all_bookings():
    async for _db in get_db_null_pool():
        await _db.bookings.delete()
        await _db.commit()


@pytest.mark.parametrize("room_id, date_from, date_to, quantity_bookings", [
    (1, "2026-08-01", "2026-08-05", 1),
    (1, "2026-08-01", "2026-08-05", 2),
    (1, "2026-08-01", "2026-08-05", 3),
])
async def test_add_and_get_bookings(
    room_id,
    date_from,
    date_to,
    quantity_bookings,
    delete_all_bookings,
    authenticated_ac,
):
    response = await authenticated_ac.post(
        url="/bookings",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to
        }
    )
    assert response.status_code == 200

    response_my_bookings = await authenticated_ac.get(url="/bookings/me")
    assert response_my_bookings.status_code == 200
    assert len(response_my_bookings.json()) == quantity_bookings
