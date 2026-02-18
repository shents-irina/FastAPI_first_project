from fastapi import FastAPI, Query, Body
import uvicorn

app = FastAPI()

hotels = [
    {"id": 1, "title": "Sochi1", "name": "sochi"},
    {"id": 2, "title": "Dubai", "name": "dubai"},
    {"id": 3, "title": "Sochi", "name": "sochi_"},
]

@app.get("/hotels")
def get_hotels(
    id: int | None = Query(None, description="айдишник"),
    title: str | None = Query(default=None, description="Название")
):
    if not id and not title:
        return hotels
    return [hotel for hotel in hotels if hotel["id"] == id or hotel["title"] == title]

@app.delete("/hotels/{hotel_id}")
def delete_hotels(
    hotel_id: int
):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {"status": "OK"}

@app.post("/hotels")
def create_hotel(
    title = Body(embed=True)
):
    global hotels
    hotels.append(
        {
            "id": hotels[-1]["id"] + 1,
            "title": title
        }
    )
    return {"status": "OK"}

@app.put(
    path="/hotels/{hotel_id}",
    summary="Замена данных отеля",
    description="Полная замена всех данных",
)
def edit_hotel(
    hotel_id: int,
    title: str = Body(),
    name: str = Body(),
):
    global hotels
    hotel = next(hotel for hotel in hotels if hotel["id"] == hotel_id)
    hotel["title"] = title
    hotel["name"] = name
    return {"status": "OK"}

@app.patch(
    path="/hotels/{hotel_id}",
    summary="Частичная замена данных отеля",
    description="Заменяем какие-то конкретные данные",
)
def partial_edit(
    hotel_id: int,
    title: str | None = Body(default=None),
    name: str | None = Body(default=None),
):
    global hotels
    hotel = next(hotel for hotel in hotels if hotel["id"] == hotel_id)
    if title:
        hotel["title"] = title
    if name:
        hotel["name"] = name
    return {"status": "OK"}

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)