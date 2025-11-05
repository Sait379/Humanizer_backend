# app/services/prompt_service.py
class PromptService:
    def __init__(self, tone: str = "neutral"):
        self.tone = tone

    def build_prompt(self, text: str) -> str:
        return f"Rewrite the following text in a {self.tone} tone:\n\n{text}"