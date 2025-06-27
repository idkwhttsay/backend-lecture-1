from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.config import settings
from src.database import create_tables
from src.tasks.api import router as tasks_router

app = FastAPI()


@app.on_event("startup")
def startup_event():
    create_tables()

@app.get("/")
def read_root():
    return {"message": f"Hello {settings.name}"}


app.include_router(tasks_router)
app.mount("/", StaticFiles(directory="src/static", html=True), name="static")