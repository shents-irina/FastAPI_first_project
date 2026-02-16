from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def func():
    return "Hello World!111"

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)