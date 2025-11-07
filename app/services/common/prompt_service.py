# app/services/prompt_service.py

class PromptService:
    def __init__(self, tone: str = "neutral"):
        self.tone = tone.lower()

    def build_prompt(self, text: str) -> str:
        """Build a tone-aware, single-output prompt for Gemini."""
        return (
            f"You are a professional writer and editor.\n"
            f"Rewrite the following text in a **{self.tone}** tone so that it sounds natural, fluent, "
            f"and written by a human. Keep the meaning the same.\n\n"
            f"Text:\n{text}\n\n"
            f"Return only one rewritten version — do not provide multiple options, explanations, or lists. "
            f"Respond with the rewritten text only."
        )