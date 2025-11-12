# app/api/v1/humanize_route.py

from fastapi import APIRouter, HTTPException
from app.schemas.humanize_schema import HumanizeRequest, HumanizeResponse
from app.services.humanize_service import HumanizeService

router = APIRouter()

@router.post("/humanize", response_model=HumanizeResponse)
async def humanize_text(payload: HumanizeRequest):
    """
    Endpoint to humanize input text using the HumanizeService pipeline.
    """
    try:
        # Initialize the orchestrator
        humanize_service = HumanizeService()

        # Run the full pipeline (normalization → masking → prompt → Gemini → grammar → scoring)
        result = await humanize_service.run_pipeline(
            text=payload.text,
            tone=payload.tone
        )

        # Return clean response
        return HumanizeResponse(**result.dict())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))