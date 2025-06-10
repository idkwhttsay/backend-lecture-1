from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.api import router as auth_router
from database import get_async_db

app = FastAPI()

app.include_router(auth_router, tags=["auth"])


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/health")
async def check_health(db: AsyncSession = Depends(get_async_db)):
    try:
        await db.execute(text("SELECT 1"))
    except OperationalError:
        raise HTTPException(
            status_code=500, detail="Database connection failed"
        )

    return {"status": "ok", "database": "connected"}
