# app/core/config.py
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "text_humanizer")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    HUMANIZER_NAME: str = os.getenv("HUMANIZER_NAME", "text_humanizer")
    GCP_PROJECT_ID : str = os.getenv("GCP_PROJECT_ID", "")
    GCP_LOCATION : str = os.getenv("GCP_LOCATION", "us-central1")

settings = Settings()