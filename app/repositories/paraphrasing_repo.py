from vertexai.generative_models import GenerativeModel
from app.services.common.prompt_service import PromptService
import time

class ParaphrasingRepo:
    def __init__(self):
        self.model = GenerativeModel("gemini-2.5-flash")

    def paraphrase(self, text: str):
        prompt = PromptService.paraphrase_prompt(text)

        start = time.time()
        resp = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.25,
                "top_p": 0.9,
                "candidate_count": 1,
            }
        )
        end = time.time()

        output_text = resp.text.strip()

        metadata = {
            "response_time_ms": round((end - start) * 1000, 2),
            "prompt_tokens": resp.usage_metadata.prompt_token_count,
            "output_tokens": resp.usage_metadata.candidates_token_count,
            "total_tokens": resp.usage_metadata.total_token_count,
        }

        return output_text, metadata
