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
        "[INSTRUCTION] Rewrite the text so it reads naturally, as if written by a clear-thinking human. "
        "Use straightforward vocabulary and short, clean sentences (average 12–18 words). "
        "Avoid stacked commas, over-formal wording, long clauses, filler phrases, or robotic transitions. "
        "Keep the tone strictly neutral—no warmth, no formality shift, no emotional coloring. Keep meaning identical. "
        "Target Flesch Reading Ease 65–80, Grade Level 7–9.\n\n"
        "Do NOT alter emojis, URLs, placeholders, quoted text, or code-like fragments.\n\n"
        "Example:\n"
        "Input: The utilization of advanced computational methodologies improves operational efficiency.\n"
        "Output: Using advanced computing methods makes work faster and easier.\n\n"
        "Text:\n{text}"
    ),

    "friendly": (
        "[INSTRUCTION] Rewrite the text in a warm, upbeat, and naturally conversational tone—like a friendly colleague. "
        "Use light positivity, natural contractions, and short, easy sentences (12–16 words). "
        "Keep meaning identical and avoid exaggeration, slang, or emotional overreach. "
        "Target Flesch Reading Ease 68–82, Grade Level 7–9.\n\n"
        "Keep emojis, URLs, and placeholders unchanged.\n\n"
        "Example:\n"
        "Input: The organization will implement a workflow optimization process on Monday.\n"
        "Output: Hey team! We’re rolling out a smoother way to get things done starting Monday.\n\n"
        "Text:\n{text}"
    ),

    "formal": (
        "[INSTRUCTION] Rewrite the text in a polished, highly structured, and formal tone suitable for academic, legal, or "
        "official communication. Avoid contractions, conversational cues, idioms, or casual phrasing. "
        "Use precise vocabulary and moderately long sentences (18–26 words). "
        "Target Grade Level 10–12, Flesch Reading Ease 45–60.\n\n"
        "Do not alter URLs, placeholders, or factual meaning.\n\n"
        "Example:\n"
        "Input: The team will start using new workflow methods on Monday.\n"
        "Output: The organization has announced that revised workflow procedures will commence on Monday.\n\n"
        "Text:\n{text}"
    ),

    "professional": (
        "[INSTRUCTION] Rewrite the text in a concise, confident, and business-professional tone. "
        "Use clear structure, direct language, and outcome-focused phrasing. "
        "Avoid corporate clichés, fluff, or overly formal academic language. "
        "Sentence length 14–20 words. Target Flesch Reading Ease 55–70, Grade Level 8–10.\n\n"
        "Do not change URLs, placeholders, metrics, or meaning.\n\n"
        "Example:\n"
        "Input: The company will introduce a new system for optimizing workflows starting Monday.\n"
        "Output: A new workflow optimization system goes live Monday for all teams.\n\n"
        "Text:\n{text}"
    ),

    "casual": (
        "[INSTRUCTION] Rewrite the text in a relaxed, natural, easygoing tone—like chatting with a friend. "
        "Use simple wording, smooth phrasing, and short sentences (10–15 words). "
        "Avoid slang, jokes, or exaggeration; keep meaning fully intact. "
        "Target Flesch Reading Ease 72–85, Grade Level 6–8.\n\n"
        "Keep emojis, placeholders, and URLs untouched.\n\n"
        "Example:\n"
        "Input: The organization will launch a workflow improvement plan next week.\n"
        "Output: Just a heads-up — the company’s rolling out a new way to work next week.\n\n"
        "Text:\n{text}"
    ),

    "empathetic": (
        "[INSTRUCTION] Rewrite the text with a warm, supportive, and understanding tone while keeping all facts accurate. "
        "Use gentle, reassuring language and short-to-medium sentences (12–18 words). "
        "Acknowledge the emotional weight subtly without adding new emotions not present in the original content. "
        "Target Flesch Reading Ease 65–80, Grade Level 7–9.\n\n"
        "Do not change URLs, placeholders, or factual content.\n\n"
        "Example:\n"
        "Input: The workflow optimization process will begin on Monday.\n"
        "Output: I know changes can feel overwhelming, but the new process starts Monday, and we’ll handle it together.\n\n"
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
            "Respond ONLY with the rewritten text, no explanations or meta-comments. and no aesterisks or quotes."
            "Fix grammar as part of rewriting."
        )

        return base_prompt + dynamic_instruction + response_format_constraint