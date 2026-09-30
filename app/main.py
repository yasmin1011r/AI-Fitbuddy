from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator"
)

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

app.include_router(router)


@app.get("/health")
def health_check():
    return {
        "status": "running",
        "project": "FitBuddy"
    }