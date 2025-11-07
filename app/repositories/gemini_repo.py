import os
from google import genai
from google.genai.types import Content, Part, GenerateContentConfig
from app.core.config import settings # Assuming this exists and contains MODEL_NAME and GEMINI_API_KEY

class GeminiRepo:
    """
    Repository for interacting with the Gemini API using the official Google GenAI SDK.
    
    This class is configured to always request three candidate strings, allowing the
    caller to select the best result for quality control.
    """

    def __init__(self):
        """Initializes the repository and the Gemini Client."""
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            # Note: This is a placeholder check. In production, API key handling
            # should use secrets management or environment variables.
            raise ValueError("❌ GEMINI_API_KEY not found in environment.")
            
        self.client = genai.Client(api_key=api_key)
        
        # Use settings model or default to the flash model
        self.model_name = settings.MODEL_NAME or "gemini-2.5-flash"

    def run_gemini(self, prompt: str) -> list[str]:
        """
        Sends a single prompt to the Gemini API and returns a list of up to three 
        rewritten candidate texts.
        
        Args:
            prompt (str): The combined instruction and text to be rewritten.
            
        Returns:
            list[str]: A list containing the rewritten texts. Returns an empty 
                       list or a list with an error message on failure.
        """
        
        # Always request 3 candidates for selection/scoring
        candidate_count = 3
        
        # Configuration for quality (Nucleus Sampling) and number of candidates
        config = GenerateContentConfig(
            temperature=0.3, 
            top_p=0.9,        
            candidate_count=candidate_count
        )
        print(f"config: {config}")
        try:
            contents = [Content(role="user", parts=[Part(text=prompt)])]

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
            )
            print(f"Gemini response: {response}")
            
            # --- CANDIDATE EXTRACTION ---
            if not response.candidates:
                return []
            
            # Extract all valid candidate texts into simple strings
            candidate_strings = []
            for candidate in response.candidates:
                # Safety check for content, parts, and text existence
                if (candidate.content and 
                    candidate.content.parts and 
                    candidate.content.parts[0].text):
                    text_to_append = str(candidate.content.parts[0].text).strip()
                    candidate_strings.append(text_to_append)
            
            # Always return the list of simple strings
            return candidate_strings
            
        except Exception as e:
            error_message = f"Error: Failed to connect or process with Gemini SDK: {e}"
    
            return [error_message]