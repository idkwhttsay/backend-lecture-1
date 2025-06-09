from fastapi import FastAPI

from .config import settings
from .tasks.api import router as tasks_router

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": f"Hello {settings.name}"}


app.include_router(tasks_router)
