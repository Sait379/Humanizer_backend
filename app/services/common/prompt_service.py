from typing import Optional
from app.services.common.scoring_service import ScoringService

class PromptService:
    """
    Builds dynamic, highly-constrained, and tone-aware prompts optimized for 
    Gemini. Each prompt includes a single-shot demonstration for in-context learning.
    """
    IDEAL_RANGES = {
        "friendly": {"flesch": (75, 100), "coleman": (8, 11)},
        "neutral": {"flesch": (65, 80), "coleman": (9, 12)},
        "formal": {"flesch": (40, 55), "coleman": (12, 15)},
        "professional": {"flesch": (55, 70), "coleman": (10, 13)},
        "casual": {"flesch": (70, 85), "coleman": (8, 11)},
        "empathetic": {"flesch": (65, 80), "coleman": (9, 12)},
    }

    DEMO_INPUT = "The company has informed its personnel that a new directive related to workflow optimization will commence on Monday."

    PROMPTS = {
    "neutral": (
    "[INSTRUCTION] Rewrite the text so it feels naturally written by a person, not by an AI or editor. "
    "Use clear, simple sentences and everyday vocabulary. "
    "Keep the meaning and tone neutral, but prefer short sentences (12–18 words average). "
    "Avoid long clauses or stacked commas. "
    "Target Flesch Reading Ease between 65 and 80, Grade Level between 7 and 9.\n\n"
    "Example:\n"
    "Input: The utilization of advanced computational methodologies improves operational efficiency.\n"
    "Output: Using advanced computing methods makes work faster and easier.\n\n"
    "Text:\n{text}"
),

    "friendly": (
        "[INSTRUCTION] Sound like a warm colleague chatting naturally. "
        "Use positive, easy language with short sentences (Flesch 65–80 range). "
        "Keep it upbeat, human, and clear while keeping the same meaning.\n\n"
        "Example:\n"
        "Input: The organization will implement a workflow optimization process on Monday.\n"
        "Output: Hey team! We’re rolling out a new way to make work smoother starting Monday.\n\n"
        "Text:\n{text}"
    ),

    "formal": (
        "[INSTRUCTION] Write in a precise, polished, and professional tone suitable for academic or official contexts. "
        "Avoid slang and contractions. Use clear structure and moderate sentence length "
        "(target Grade 10–12 readability, Flesch 50–65).\n\n"
        "Example:\n"
        "Input: The team will start using new workflow methods on Monday.\n"
        "Output: The organization has announced that workflow optimization measures will commence on Monday.\n\n"
        "Text:\n{text}"
    ),

    "professional": (
        "[INSTRUCTION] Rewrite with a confident, business-like tone. "
        "Keep it concise, clear, and results-focused (Grade 8–10, Flesch 60–75). "
        "Avoid fluff; sound like corporate communication done right.\n\n"
        "Example:\n"
        "Input: The company will introduce a new system for optimizing workflows starting Monday.\n"
        "Output: A new workflow optimization policy begins Monday for all teams.\n\n"
        "Text:\n{text}"
    ),

    "casual": (
        "[INSTRUCTION] Make it sound relaxed and easy, like talking to a friend. "
        "Use simple words and short sentences (Flesch 70–85). "
        "Keep it friendly and clear, but don’t overdo slang.\n\n"
        "Example:\n"
        "Input: The organization will launch a workflow improvement plan next week.\n"
        "Output: Hey, just letting you know — the company’s rolling out a new way to work next week.\n\n"
        "Text:\n{text}"
    ),

    "empathetic": (
        "[INSTRUCTION] Rewrite with empathy and warmth. "
        "Use gentle, caring language that’s easy to read (Flesch 65–80). "
        "Show understanding while keeping the facts accurate.\n\n"
        "Example:\n"
        "Input: The workflow optimization process will begin on Monday.\n"
        "Output: We know changes can be a lot, but the new process starts Monday — and we’ll support you all the way.\n\n"
        "Text:\n{text}"
    ),
}



    ALLOWED_TONES = set(PROMPTS.keys())

    def __init__(self, tone: str = None):
        """Initializes the service with a tone, defaulting to 'neutral'."""
        self.tone = tone.lower().strip() if tone else "neutral"
        if self.tone not in self.ALLOWED_TONES:
            print(f"Warning: Tone '{self.tone}' not supported. Defaulting to 'neutral'.")
            self.tone = "neutral"

    def build_prompt(self, text, tone: Optional[str] = None) -> str:
        """
        Builds the final prompt, appending the strict single-shot output constraint
        after the role and demonstration are defined.
        """
        # Handle list input safely
        if isinstance(text, list):
            text = " ".join(map(str, text))

        # Normalize dynamic tone override
        tone = tone.lower().strip() if tone else self.tone
        if tone not in self.ALLOWED_TONES:
            print(f"Warning: Tone '{tone}' not supported. Defaulting to 'neutral'.")
            tone = "neutral"

        # Build base prompt
        base_prompt = self.PROMPTS[tone].format(text=text.strip())

        # Add response format constraint
        response_format_constraint = (
            "\n\n--- RESPONSE FORMAT ---\n"
            "Response MUST contain ONLY the rewritten text.\n"
            "Do not include any introductory phrases, explanations, or added commentary."
        )

        return base_prompt + response_format_constraint
    
    def build_dynamic_prompt(self, text: str, tone: str):
        """
        Dynamically adjusts the rewriting instructions based on readability metrics.
        """
        scoring_service = ScoringService()
        metrics = scoring_service.evaluate_preprocessed_text(text)
        tone = tone.lower().strip() if tone in self.ALLOWED_TONES else "neutral"

        ideal = self.IDEAL_RANGES.get(tone, {"flesch": (60, 75), "coleman": (9, 12)})
        adjustments = []

        # --- Evaluate readability gaps ---
        if metrics["flesch_reading_ease"] < ideal["flesch"][0]:
            adjustments.append("Simplify vocabulary and shorten sentences.")
        elif metrics["flesch_reading_ease"] > ideal["flesch"][1]:
            adjustments.append("Add structure and use more precise terms.")

        if metrics["coleman_liau_index"] > ideal["coleman"][1]:
            adjustments.append("Reduce word complexity and avoid long clauses.")
        elif metrics["coleman_liau_index"] < ideal["coleman"][0]:
            adjustments.append("Introduce richer sentence structures and vocabulary.")

        guidance = " ".join(adjustments) if adjustments else "Maintain clarity and tone balance."

        # --- Merge into the base tone template ---
        base_prompt = self.PROMPTS.get(tone, self.PROMPTS["neutral"]).format(text=text.strip())
        dynamic_instruction = f"\n\n[ADAPTIVE GUIDANCE]\n{guidance}\nTarget Flesch: {ideal['flesch'][0]}–{ideal['flesch'][1]}, Coleman–Liau: {ideal['coleman'][0]}–{ideal['coleman'][1]}."

        response_format_constraint = (
            "\n\n--- RESPONSE FORMAT ---\n"
            "Respond ONLY with the rewritten text, no explanations or meta-comments."
        )

        return base_prompt + dynamic_instruction + response_format_constraint