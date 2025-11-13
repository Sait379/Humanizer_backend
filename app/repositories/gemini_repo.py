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

    def get_config_for_tone(self, tone: str) -> GenerateContentConfig:
        """
        Returns tone-aware configuration for generation settings.
        """
        tone = tone.lower().strip()
        tone_configs = {
        "friendly":   {"temperature": 0.7, "top_p": 0.95, "top_k": 40},
        "neutral":    {"temperature": 0.4, "top_p": 0.9,  "top_k": 30},
        "formal":     {"temperature": 0.3, "top_p": 0.85, "top_k": 20},
        "empathetic": {"temperature": 0.65,"top_p": 0.9,  "top_k": 40},
        "professional":{"temperature":0.35,"top_p": 0.85, "top_k": 25},
        "casual":     {"temperature": 0.8, "top_p": 0.95, "top_k": 50},
        }

        cfg = tone_configs.get(tone, tone_configs["neutral"])
        return GenerateContentConfig(
            temperature=cfg["temperature"],
            top_k=cfg["top_k"],
            top_p=cfg["top_p"]
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
            config = self.get_config_for_tone(tone)
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
