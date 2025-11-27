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

    placeholder_rule = """
    Keep ALL bracketed placeholders exactly as they are. 
    Do NOT change their text, characters, digits, spacing, order, or position.
    Return every placeholder (e.g., [[HASH:xxxx]], [URL_1], [EMOJI_1]) unchanged.
    """

    PROMPTS = {
    "{TONE}": (
        "[INSTRUCTION] Rewrite the text so it feels written by a real human — not an AI. "
        "Maintain meaning exactly, but increase natural variation: shift sentence lengths, use slightly irregular rhythm, "
        "allow micro-pauses inside the paragraphs (like 'well,' 'also,' 'honestly,'), not at starting if tone is not Formal or Professional and incorporate subtle hedges ('a bit', 'kind of'). "
        "Increase lexical unpredictability without changing facts. Avoid robotic symmetry.\n\n"

        "[HUMAN BURSTINESS]\n"
        "Use a mix of short and long sentences. Alternate pacing. Use natural breaks, clause-level variation, "
        "and occasional informal connectors that humans use when thinking while writing. "
        "Avoid perfect grammar uniformity. Keep flow organic.\n\n"

        "[STYLE SAFETY]\n"
        "No spelling errors. No grammar mistakes that change meaning. Never alter numbers, years, dates, "
        "ages, IDs, amounts, or placeholders. Preserve ALL formatting: new lines, *, markdown, bullets, URLs, emojis.\n\n"

        "[TONE]\n"
        "{TONE_SPECIFIC}\n\n"

        "Text:\n{text}"
    )
}

    TONE_MAP = {
    "neutral": "Keep tone plain, balanced, and natural. Avoid warmth or emotion.",
    "friendly": "Use warm flow, soft edges, light positivity, natural contractions.",
    "formal": "Keep it refined but human, with slightly complex structure.",
    "professional": "Confident, concise, but still human and slightly varied.",
    "casual": "Relaxed, chatty feel; small pauses and informal flow.",
    "empathetic": "Soft, understanding, supportive tone with emotional steadiness."
}



    ALLOWED_TONES = set(PROMPTS.keys())

    def __init__(self, tone: str = None):
        """Initializes the service with a tone, defaulting to 'neutral'."""
        self.tone = tone.lower().strip() if tone else "neutral"
        if self.tone not in self.ALLOWED_TONES:
            print(f"Warning: Tone '{self.tone}' not supported. Defaulting to 'neutral'.")
            self.tone = "neutral"

    def build_prompt(self, text, tone=None):
        if isinstance(text, list):
            text = " ".join(map(str, text))

        tone = tone.lower().strip() if tone else self.tone
        if tone not in self.ALLOWED_TONES:
            tone = "neutral"

        tone_specific = {
            "neutral": "Use clear, simple language with light human variation.",
            "friendly": "Warm, easy language with soft transitions.",
            "formal": "Polished sentences with natural variety (not robotic).",
            "professional": "Concise but human; vary rhythm for natural feel.",
            "casual": "Loose, relaxed flow, natural pauses.",
            "empathetic": "Gentle, understanding, mild warmth."
        }.get(tone)

        prompt = self.PROMPTS["{TONE}"] \
            .replace("{TONE_SPECIFIC}", tone_specific) \
            .replace("{TONE}", tone) \
            .format(text=text.strip())

        # Output constraint
        return (
            prompt + self.placeholder_rule + 
            "\n\n[OUTPUT]\nReturn ONLY the rewritten text. Do not explain anything."
        )

    
    def build_dynamic_prompt(self, text, tone):
        scoring_service = ScoringService()
        metrics = scoring_service.evaluate_preprocessed_text(text)

        tone = tone.lower().strip() if tone in self.ALLOWED_TONES else "neutral"

        ideal = self.IDEAL_RANGES[tone]
        adjustments = []

        # If too simple → add structure (increase burstiness)
        if metrics["flesch_reading_ease"] > ideal["flesch"][1]:
            adjustments.append("Add richer phrasing and occasional longer sentences.")

        # If too complex → simplify
        if metrics["coleman_liau_index"] > ideal["coleman"][1]:
            adjustments.append("Use simpler words and break long clauses.")

        # If too flat → increase burstiness
        if metrics["lexical_diversity"] < 0.35:
            adjustments.append("Increase lexical variety slightly.")

        guidance = " ".join(adjustments) if adjustments else "Maintain balanced human-like variation."

        base = self.build_prompt(text, tone)

        burstiness_block = (
            "\n\n[BURSTINESS BOOST]\n"
            "Introduce natural variation — mix of short and long sentences, unexpected but meaningful clause boundaries, "
            "human-like pacing shifts, and light cognitive markers like 'well,' 'also,' or 'honestly,'. "
            "Avoid robotic parallelism.\n"
        )

        readability_block = (
            f"[READABILITY TARGET]\n{guidance} "
            f"(Flesch target: {ideal['flesch'][0]}–{ideal['flesch'][1]}, "
            f"Coleman-Liau: {ideal['coleman'][0]}–{ideal['coleman'][1]}.)"
        )

        return base + burstiness_block + self.placeholder_rule + readability_block
    # -------------------------------------------------------------------------
    # SIMPLE PARAPHRASE PROMPT
    # -------------------------------------------------------------------------
    @staticmethod
    def paraphrase_prompt(text: str) -> str:
        return (
            "Paraphrase the given text without altering its meaning.\n"
            "Keep the wording concise and natural.\n"
            "Return only one rewritten version.\n\n"
            f"{text}"
        )