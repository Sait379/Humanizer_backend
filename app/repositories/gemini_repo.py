import logging
import time
from typing import Optional

import vertexai
from vertexai import generative_models
from vertexai.generative_models import GenerationConfig as VertexGenerationConfig

from app.core.config import settings  # must define GCP_PROJECT_ID, GCP_LOCATION, MODEL_NAME

logger = logging.getLogger(__name__)


class GeminiRepo:
    """
    Vertex AI–native repository for Gemini models.

    - Uses vertexai.init() (service account / ADC auth)
    - Uses GenerativeModel for text-only endpoints
    - Enforces model safety
    - Adds retries + backoff
    - Returns best text output
    """

    ALLOWED_MODELS = {
        "gemini-2.5-flash",
        "gemini-2.5-flash-001",
        "gemini-1.5-flash",
    }

    DISALLOWED_SUBSTRINGS = [
        "image", "imagen", "video", "vision", "audio", "speech",
        "embed", "multimodal", "agent", "tuning",
    ]

    def __init__(self):
        project = getattr(settings, "GCP_PROJECT_ID", None)
        location = getattr(settings, "GCP_LOCATION", "us-central1")

        if not project:
            raise ValueError("GCP_PROJECT_ID is required for Vertex AI.")

        vertexai.init(project=project, location=location)

        configured_model = getattr(settings, "MODEL_NAME", "gemini-2.5-flash")
        external_safe_models = getattr(settings, "SAFE_VERTEX_MODELS", None)

        if external_safe_models and isinstance(external_safe_models, (list, set, tuple)):
            self.SAFE_MODELS = set(external_safe_models)
        else:
            self.SAFE_MODELS = set(self.ALLOWED_MODELS)

        self.model_name = self._validate_model_name(configured_model)
        self.model = generative_models.GenerativeModel(self.model_name)

        self.max_retries = 3
        self.base_backoff = 0.7

    def _validate_model_name(self, model_name: str) -> str:
        name = (model_name or "").strip()
        if not name:
            logger.warning("Empty MODEL_NAME. Using gemini-2.5-flash.")
            return "gemini-2.5-flash"

        lowered = name.lower()
        for bad in self.DISALLOWED_SUBSTRINGS:
            if bad in lowered:
                raise ValueError(f"Model '{name}' is blocked (contains '{bad}').")

        if name not in self.SAFE_MODELS:
            logger.warning(f"MODEL_NAME '{name}' not in SAFE_MODELS={self.SAFE_MODELS}. Using gemini-2.5-flash.")
            return "gemini-2.5-flash"

        return name

    def get_config_for_tone(self, tone: Optional[str] = None) -> VertexGenerationConfig:
        t = (tone or "neutral").lower().strip()

        tone_configs = {
            "friendly":     {"temperature": 0.82, "top_p": 0.96, "top_k": 32},
            "casual":       {"temperature": 0.9,  "top_p": 0.98, "top_k": 40},
            "empathetic":   {"temperature": 0.8,  "top_p": 0.95, "top_k": 32},
            "professional": {"temperature": 0.65, "top_p": 0.90, "top_k": 24},
            "formal":       {"temperature": 0.55, "top_p": 0.85, "top_k": 24},
            "neutral":      {"temperature": 0.70, "top_p": 0.92, "top_k": 24},
        }

        cfg = tone_configs.get(t, tone_configs["neutral"])

        return VertexGenerationConfig(
            temperature=cfg["temperature"],
            top_p=cfg["top_p"],
            top_k=cfg["top_k"],
        )

    def run_gemini(self, prompt: str, tone: Optional[str] = None) -> str:
        gen_config = self.get_config_for_tone(tone)

        last_err = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"[VERTEX] Calling model={self.model_name}, attempt={attempt}")

                response = self.model.generate_content(
                    prompt,
                    generation_config=gen_config,
                )

                usage = getattr(response, "usage_metadata", None)
                if usage:
                    logger.info(f"[TOKENS] usage_metadata={usage}")

                text = self._extract_text(response)
                if not text:
                    raise RuntimeError("Empty text returned from Vertex AI.")

                if len(text) > 20000:
                    logger.warning(f"[VERTEX] Truncating output from {len(text)} to 20000 chars.")
                    text = text[:20000]

                return text

            except Exception as e:
                last_err = e
                msg = str(e).lower()

                if any(x in msg for x in ["invalid_argument", "permission_denied", "not_found"]):
                    logger.error(f"[VERTEX] Non-retryable error: {e}")
                    raise

                if attempt == self.max_retries:
                    logger.exception(f"[VERTEX] Failed after {attempt} attempts: {e}")
                    break

                backoff = self.base_backoff * attempt
                logger.warning(f"[VERTEX] Transient error: {e}. Retrying in {backoff:.2f}s...")
                time.sleep(backoff)

        raise RuntimeError(f"Vertex call failed after {self.max_retries} attempts: {last_err}")

    @staticmethod
    def _extract_text(response) -> str:
        if not response or not getattr(response, "candidates", None):
            return ""

        first = response.candidates[0]
        parts = []
        for part in getattr(first, "content", {}).parts:
            if hasattr(part, "text") and part.text:
                parts.append(part.text)

        return "".join(parts).strip()