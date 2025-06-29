from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from src.database import create_db_and_tables

from src.config import settings
from src.tasks.controller import router as tasks_router
from src.auth.controller import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": f"Hello {settings.name}"}


app.include_router(tasks_router)
app.include_router(auth_router)
app.mount("/", StaticFiles(directory="src/static", html=True), name="static")
