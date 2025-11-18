import os
from google import genai
from google.genai.types import Content, Part, GenerateContentConfig
from app.core.config import settings  # Ensure this holds MODEL_NAME and GEMINI_API_KEY


class GeminiRepo:
    """
    Repository for interacting with the Gemini API using the official Google GenAI SDK.
    
    This class now requests **a single best output** from Gemini, relying on the model's
    built-in quality ranking instead of fetching multiple candidates.
    """

    def __init__(self):
        """Initializes the repository and Gemini client."""
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in environment variables.")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = settings.MODEL_NAME or "gemini-2.5-flash"

    def get_config_for_tone(self, tone: str, input_text: str = "") -> GenerateContentConfig:
        tone = tone.lower().strip()

        # Human-texture-aware sampling
        tone_configs = {
            "friendly":     {"temperature": 0.82, "top_p": 0.96, "top_k": 40},
            "casual":       {"temperature": 0.88, "top_p": 0.97, "top_k": 55},
            "empathetic":   {"temperature": 0.78, "top_p": 0.94, "top_k": 40},
            "neutral":      {"temperature": 0.55, "top_p": 0.90, "top_k": 32},
            "professional": {"temperature": 0.48, "top_p": 0.87, "top_k": 28},
            "formal":       {"temperature": 0.42, "top_p": 0.84, "top_k": 20},
        }


        cfg = tone_configs.get(tone, tone_configs["neutral"])

        # Slight dynamic adjustment by text length
        words = len(input_text.split())

        if words < 20:
            cfg["top_k"] += 8
        elif words > 150:
            cfg["top_k"] -= 5

        cfg["top_k"] = max(10, min(cfg["top_k"], 75))

        return GenerateContentConfig(
            temperature=cfg["temperature"],
            top_p=cfg["top_p"],
            top_k=cfg["top_k"],
        )

    def run_gemini(self, prompt: str, tone: str) -> str:
        """
        Sends a single prompt to the Gemini API and returns the best rewritten text.
        
        Args:
            prompt (str): The text prompt or instruction to humanize.
            tone (str): Desired tone ("friendly", "neutral", "formal", etc.)
            
        Returns:
            str: The best rewritten output text from Gemini.
        """
        try:
            
            config = self.get_config_for_tone(tone, input_text=prompt)
            contents = [Content(role="user", parts=[Part(text=prompt)])]

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
            )

            # Gemini already returns the top-ranked response by default.
            # Safely extract its text.
            if not response or not getattr(response, "text", None):
                return "⚠️ Gemini returned no text output."

            return response.text.strip()

        except Exception as e:
            return f"❌ Error while calling Gemini API: {str(e)}"
