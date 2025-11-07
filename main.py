# app/main.py
from fastapi import FastAPI
from app.api.v1.humanize_route import router as humanize_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(humanize_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": f"{settings.HUMANIZER_NAME} API is running!"}