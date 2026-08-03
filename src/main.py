from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from api.auth import router as router_auth
from api.bookings import router as router_bookings
from api.hotels import router as router_hotels
from api.rooms import router as router_rooms
from api.facilities import router as router_facilities
from init import redis_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    yield
    await redis_manager.close()

app = FastAPI(lifespan=lifespan)

app.include_router(router_auth)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_facilities)
app.include_router(router_bookings)

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
