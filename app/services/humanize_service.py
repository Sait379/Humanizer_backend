# app/services/humanize_service.py

import time
import logging
from app.services.common.normalize_service import NormalizeService
from app.schemas.humanize_schema import HumanizeResponse
from app.services.common.prompt_service import PromptService
from app.repositories.gemini_repo import GeminiRepo
from app.services.common.scoring_service import ScoringService

logger = logging.getLogger(__name__)


class HumanizeService:
    """
    Orchestrates the full text humanization pipeline.
    Each stage of the pipeline performs a key transformation step.
    """

    def __init__(self):
        # Initialize dependent services
        self.normalize_service = NormalizeService()
        self.prompt_service = PromptService()
        self.gemini_repo = GeminiRepo()
        self.scoring_service = ScoringService()

    async def run_pipeline(self, text: str, tone: str = "neutral") -> HumanizeResponse:
        start_time = time.perf_counter()  # Start timing the full pipeline
        try:

            # 🧹 STEP 1: Text Normalization
            clean_text = self.normalize_service.clean_and_normalize(text)
            print(f"Clean text : {clean_text['cleaned_text']}")
            logger.debug("[CLEAN] Cleaned text ready for prompt build.")

            # 🧩 STEP 2: PII Masking (Optional / Future Feature)
            # masked_text, pii_map = self.pii_service.mask_pii(clean_text)
            # masked_text = clean_text["cleaned_text"]

            # 🧠 STEP 3: Prompt Construction
            final_prompt = self.prompt_service.build_dynamic_prompt(
                clean_text["cleaned_text"], tone
            )

            # 🤖 STEP 4: Gemini Model Invocation
            best_output = self.gemini_repo.run_gemini(final_prompt, tone)
            logger.debug("[GEMINI] Response received successfully.")

            # 🪄 STEP 5: Postprocessing (PII Restore / Grammar Fix / Emoji Restoring)
            final_output = self.normalize_service.restore(best_output, clean_text["mask_map"])
            print(f"Final output : {final_output}")

            # 📊 STEP 6: Scoring & Quality Evaluation
       
            score = self.scoring_service.evaluate_postprocessed_text(final_output)
            logger.info(f"[SCORE] Flesch={score['flesch_reading_ease']} | Overall={score['overall_score']}")

          
            # ⏱️ STEP 7: Compute Response Time
    
            end_time = time.perf_counter()
            response_time = round(end_time - start_time, 3)  # seconds

            # ✅ STEP 8: Build and Return Response
            return HumanizeResponse(
                input_length=len(text),
                humanized_text=final_output,
                score=score,
                response_time_in_seconds=response_time,
                model=self.gemini_repo.model_name,
                tone=tone,
                message="Processed via Gemini pipeline."
            )

        except Exception as e:
 
            # ❌ ERROR HANDLING
            end_time = time.perf_counter()
            response_time = round(end_time - start_time, 3)

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