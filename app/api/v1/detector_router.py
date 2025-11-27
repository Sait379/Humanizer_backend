from fastapi import APIRouter
from pydantic import BaseModel
from app.services.detector.detector_service import DetectorService

router = APIRouter(prefix="/api/detector", tags=["AI Detector"])

class DetectorInput(BaseModel):
    text: str

detector_service = DetectorService()

@router.post("/analyze")
async def analyze_text(payload: DetectorInput):
    return detector_service.analyze(payload.text)
