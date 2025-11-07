# app/schemas/humanize_schema.py
from asyncio.windows_events import NULL
from pydantic import BaseModel
from typing import Optional

class HumanizeRequest(BaseModel):
    text: str
    tone: str = "neutral"

class HumanizeResponse(BaseModel):
    input_length: Optional[int] = None
    humanized_text: list[str] = None
    score: Optional[str] = None
    model: Optional[str] = None
    tone: Optional[str] = None
    error: Optional[str] = None
    message: Optional[str] = None
