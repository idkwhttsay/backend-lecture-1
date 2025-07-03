from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from src.database import create_db_and_tables, SessionDep
from src.redis import check_redis_connection

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

@app.get("/health")
async def health(db: SessionDep):
    try:
        db.execute(text("SELECT 1"))
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection failed")

    redis_connection_status = "connected" if check_redis_connection() else "disconnected"

    return {
        "status": "OK",
        "database": "connected",
        "redis": redis_connection_status,
    }

app.include_router(tasks_router)
app.include_router(auth_router)
app.mount("/", StaticFiles(directory="src/static", html=True), name="static")
