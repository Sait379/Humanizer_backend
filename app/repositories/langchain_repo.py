# app/repositories/langchain_repo.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage
from app.core.config import settings

class LangChainRepo:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("❌ GEMINI_API_KEY not found in environment.")
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GEMINI_API_KEY
        )

    def run_gemini(self, prompt: str) -> str:
        """Send prompt to Gemini and return response."""
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content