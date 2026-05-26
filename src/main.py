from fastapi import FastAPI
import uvicorn

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from api.auth import router as router_auth
from api.hotels import router as router_hotels

app = FastAPI()

app.include_router(router_auth)
app.include_router(router_hotels)

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)