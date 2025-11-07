# app/services/humanize_service.py

# from app.services.normalize_service import NormalizeService
# from app.services.pii_service import PIIService
from click import prompt
from app.schemas.humanize_schema import HumanizeResponse
from app.services.common.prompt_service import PromptService
from app.repositories.gemini_repo import GeminiRepo   # ✅ replaced here
# from app.services.scoring_service import ScoringService
# from app.services.grammar_service import GrammarService


class HumanizeService:
    """
    Orchestrates the full text humanization pipeline.
    """

    def __init__(self):
        # self.normalize_service = NormalizeService()
        # self.pii_service = PIIService()
        self.prompt_service = PromptService()
        self.gemini_repo = GeminiRepo()               # ✅ uses Gemini now
        # self.scoring_service = ScoringService()
        # self.grammar_service = GrammarService()

    async def run_pipeline(self, text: str, tone: str = "neutral"):
        """
        Executes the end-to-end pipeline using Gemini API.
        """
        try:
            # Step 1: Normalize text
            # clean_text = self.normalize_service.clean_text(text)

            # Step 2: Mask PII
            # masked_text, pii_map = self.pii_service.mask_pii(clean_text)

            # Step 3: Build prompt (tone-aware)
            prompt = self.prompt_service.build_prompt(text, tone)

            # Step 4: Send to Gemini
            model_output =  self.gemini_repo.run_gemini(prompt)

            # Step 5: Restore PII
            # restored_output = self.pii_service.restore_pii(model_output, pii_map)

            # Step 6: Grammar correction
            # grammatically_fixed = self.grammar_service.correct_text(restored_output)

            # Step 7: Evaluate scoring
            # score = self.scoring_service.evaluate_text(grammatically_fixed)

            return HumanizeResponse(
                input_length=len(text),
                humanized_text=model_output,
                score= None,
                model=self.gemini_repo.model_name,
                tone=tone
            )

        except Exception as e:
            return HumanizeResponse(
                input_length=len(text),
                humanized_text="",
                model=self.gemini_repo.model_name,
                tone=tone,
                score=None,
                error=str(e),
                message="Pipeline failed during humanization"
            )

