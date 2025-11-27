from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.paraphrase_service import ParaphraseService

router = APIRouter()
paraphrase_service = ParaphraseService()

class ParaphraseRequest(BaseModel):
    text: str

@router.post("/paraphrase")
async def paraphrase_text(payload: ParaphraseRequest):
    """
    Paraphrases the given text using the ParaphraseService.
    """
    try:
        paraphrased, meta = paraphrase_service.run(payload.text)

        return {
            "paraphrased_text": paraphrased,
            "metadata": meta
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
