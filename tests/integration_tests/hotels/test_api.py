async def test_get_hotels(ac):
    response = await ac.get(
        url="/hotels",
        params={
            "date_from": "2026-08-01",
            "date_to": "2026-08-05"
        }
    )
    assert response.status_code == 200
