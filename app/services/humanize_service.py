# app/services/humanize_service.py
import time
from app.services.common.normalize_service import NormalizeService
from app.schemas.humanize_schema import HumanizeResponse
from app.services.common.prompt_service import PromptService
from app.repositories.gemini_repo import GeminiRepo
from app.services.common.scoring_service import ScoringService
import logging

logger = logging.getLogger(__name__)


class HumanizeService:

    def __init__(self):
        self.normalize_service = NormalizeService()
        self.prompt_service = PromptService()
        self.gemini_repo = GeminiRepo()
        self.scoring_service = ScoringService()

    async def run_pipeline(self, text: str, tone: str = "neutral") -> HumanizeResponse:
        start_time = time.perf_counter()  # Start timing
        try:

            # --- 2️⃣ Preprocess ---
            clean_text = self.normalize_service.clean_and_normalize(text)
            logger.debug(f"[CLEAN] Cleaned text ready for prompt build.")

            # --- 3️⃣ Build Prompt ---
            final_prompt = self.prompt_service.build_dynamic_prompt(
                clean_text["cleaned_text"], tone
            )

            # --- 4️⃣ Gemini Rewrite ---
            best_output = self.gemini_repo.run_gemini(final_prompt, tone)
            logger.debug(f"[GEMINI] Response received successfully.")

            # --- 5️⃣ Postprocess + Score ---
            score = self.scoring_service.evaluate_postprocessed_text(best_output)
            logger.info(f"[SCORE] Flesch={score['flesch_reading_ease']} | Overall={score['overall_score']}")

            end_time = time.perf_counter()  # End timing
            response_time = round(end_time - start_time, 3)  # in seconds

            return HumanizeResponse(
                input_length=len(text),
                humanized_text=best_output,
                score=score,
                response_time_in_seconds=response_time,
                model=self.gemini_repo.model_name,
                tone=tone,
                message="Processed via Gemini pipeline."
            )

        except Exception as e:
            logger.exception(f"Pipeline failed: {e}")
            return HumanizeResponse(
                input_length=len(text),
                humanized_text="",
                model=getattr(self.gemini_repo, "model_name", "unknown"),
                tone=tone,
                score=None,
                response_time_in_seconds=response_time,
                error=str(e),
                message="Pipeline failed during humanization."
            )