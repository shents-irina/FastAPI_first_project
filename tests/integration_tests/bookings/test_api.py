import pytest


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
