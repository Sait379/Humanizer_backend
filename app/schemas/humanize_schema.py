# app/schemas/humanize_schema.py
from pydantic import BaseModel

class HumanizeRequest(BaseModel):
    text: str
    tone: str = "neutral"

class HumanizeResponse(BaseModel):
    result: str