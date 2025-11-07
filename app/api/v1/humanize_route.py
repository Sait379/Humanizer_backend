# app/api/v1/humanize_route.py
from fastapi import APIRouter, HTTPException
from app.schemas.humanize_schema import HumanizeRequest, HumanizeResponse
from app.services.common.prompt_service import PromptService
from app.repositories.langchain_repo import LangChainRepo

router = APIRouter()

@router.post("/humanize", response_model=HumanizeResponse)
async def humanize_text(payload: HumanizeRequest):
    try:
        prompt_service = PromptService(tone=payload.tone)
        prompt = prompt_service.build_prompt(payload.text)

        langchain_repo = LangChainRepo()
        result = langchain_repo.run_gemini(prompt)

        return HumanizeResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))