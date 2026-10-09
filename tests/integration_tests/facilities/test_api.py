async def test_get_facilities(ac):
    response = await ac.get("/facilities")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_add_facility(ac):
    facility_title = "Удобство для добавления"
    response = await ac.post(
        "/facilities",
        json={"title": facility_title},
    )
    assert response.status_code == 200
    res = response.json()
    assert isinstance(res, dict)
    assert "data" in res
    assert res["data"]["title"] == facility_title


async def test_new_facility_in_list(ac):
    facility_title = "Новое удобство"
    create_response = await ac.post("/facilities", json={"title": facility_title})
    assert create_response.status_code == 200

    list_response = await ac.get("/facilities")
    titles = [facility["title"] for facility in list_response.json()]
    assert facility_title in titles


async def test_create_duplicate_facility_returns_409(ac):
    payload = {"title": "Уникальное удобство"}

    first_response = await ac.post("/facilities", json=payload)
    assert first_response.status_code == 200

    second_response = await ac.post("/facilities", json=payload)
    assert second_response.status_code == 409


async def test_delete_facility(ac):
    create_response = await ac.post("/facilities", json={"title": "Удобство для удаления"})
    facility_id = create_response.json()["data"]["id"]

    delete_response = await ac.delete(f"/facilities/{facility_id}")
    assert delete_response.status_code == 200

    list_response = await ac.get("/facilities")
    facility_ids = [facility["id"] for facility in list_response.json()]
    assert facility_id not in facility_ids


async def test_delete_nonexistent_facility_returns_404(ac):
    response = await ac.delete("/facilities/999999")
    assert response.status_code == 404
