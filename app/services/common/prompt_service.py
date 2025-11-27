# app/services/common/prompt_service.py

from typing import Optional
from app.services.common.scoring_service import ScoringService


class PromptService:
    """
    Builds dynamic, highly-constrained, and tone-aware prompts optimized
    for Gemini on Vertex AI. Designed for text humanization.
    """

    IDEAL_RANGES = {
        "friendly": {"flesch": (75, 100), "coleman": (8, 11)},
        "neutral": {"flesch": (65, 80), "coleman": (9, 12)},
        "formal": {"flesch": (40, 55), "coleman": (12, 15)},
        "professional": {"flesch": (55, 70), "coleman": (10, 13)},
        "casual": {"flesch": (70, 85), "coleman": (8, 11)},
        "empathetic": {"flesch": (65, 80), "coleman": (9, 12)},
    }

    DEMO_INPUT = (
        "The company has informed its personnel that a new directive related to workflow "
        "optimization will commence on Monday."
    )

    placeholder_rule = """[PLACEHOLDER RULE]
Keep ALL bracketed placeholders exactly as they are.
Do NOT change their text, characters, digits, SALT suffixes (like _KX), spacing, order, or position.
Return every placeholder (e.g., [[HASH:xxxx]], ###[[HASH:xxxx]]###, [URL_1_KX], [EMOJI_1_KX]) unchanged.
Never add or remove brackets around existing placeholders.
Never replace placeholders with descriptions or natural language.
"""

    PROMPTS = {
        "{TONE}": (
            "[INSTRUCTION]\n"
            "Rewrite the text so it feels written by a real human — not an AI. "
            "Maintain meaning exactly, but increase natural variation: shift sentence lengths, "
            "use slightly irregular rhythm, allow micro-pauses (like 'well,' 'also,' 'honestly,'), "
            "and incorporate subtle hedges ('a bit', 'kind of'). Increase lexical unpredictability "
            "without changing facts. Avoid robotic symmetry.\n\n"

            "[HUMAN BURSTINESS]\n"
            "Use a mix of short and long sentences. Alternate pacing. Use natural breaks, "
            "clause-level variation, and occasional informal connectors that humans use when "
            "thinking while writing. Avoid perfect grammar uniformity. Keep the flow organic.\n\n"

            "[STYLE SAFETY]\n"
            "No spelling errors. No grammar mistakes that change meaning. Never alter numbers, years, "
            "dates, ages, IDs, amounts, or placeholders. Preserve ALL formatting: new lines, *, markdown, "
            "bullets, URLs, and emojis.\n\n"

            "{PLACEHOLDER_RULE}\n\n"

            "[TONE]\n"
            "{TONE_SPECIFIC}\n\n"

            "[TEXT TO REWRITE]\n"
            "{text}\n\n"

            "[OUTPUT CONSTRAINT]\n"
            "Return ONLY the rewritten text, with the same placeholders and numeric values preserved. "
            "Do not add explanations, headers, extra commentary, or metadata.\n"
        )
    }

    TONE_MAP = {
        "neutral": "Use clear, simple language with light human variation.",
        "friendly": "Use warm flow, soft edges, light positivity, natural contractions.",
        "formal": "Keep it refined but human, with slightly complex structure.",
        "professional": "Confident, concise, but still human and slightly varied.",
        "casual": "Relaxed, chatty feel; small pauses and informal flow.",
        "empathetic": "Soft, understanding, supportive tone with emotional steadiness.",
    }

    # ✅ allowed tones = actual tones we support
    ALLOWED_TONES = set(TONE_MAP.keys())

    def __init__(self, tone: Optional[str] = None):
        """Initializes the service with a tone, defaulting to 'neutral'."""
        self.tone = tone.lower().strip() if tone else "neutral"
        if self.tone not in self.ALLOWED_TONES:
            print(f"Warning: Tone '{self.tone}' not supported. Defaulting to 'neutral'.")
            self.tone = "neutral"

    def build_prompt(self, text, tone: Optional[str] = None) -> str:
        """
        Build a base prompt using the selected tone and core instructions.
        """
        if isinstance(text, list):
            text = " ".join(map(str, text))

        tx = (tone or self.tone) or "neutral"
        tx = tx.lower().strip()
        if tx not in self.ALLOWED_TONES:
            tx = "neutral"

        tone_specific = self.TONE_MAP.get(tx, self.TONE_MAP["neutral"])

        base_template = self.PROMPTS["{TONE}"]
        prompt = (
            base_template
            .replace("{TONE_SPECIFIC}", tone_specific)
            .replace("{TONE}", tx)
            .replace("{PLACEHOLDER_RULE}", self.placeholder_rule)
            .format(text=str(text).strip())
        )

        return prompt

    def build_dynamic_prompt(self, text: str, tone: str) -> str:
        """
        Builds a prompt augmented with readability/burstiness guidance derived
        from ScoringService metrics for the input text.
        """
        scoring_service = ScoringService()
        metrics = scoring_service.evaluate_preprocessed_text(text)

        t = tone.lower().strip() if tone else "neutral"
        if t not in self.ALLOWED_TONES:
            t = "neutral"

        ideal = self.IDEAL_RANGES[t]
        adjustments = []

        # If too simple → add structure (increase complexity/burstiness)
        if metrics["flesch_reading_ease"] > ideal["flesch"][1]:
            adjustments.append("Add richer phrasing and occasional longer sentences.")

        # If too complex → simplify
        if metrics["coleman_liau_index"] > ideal["coleman"][1]:
            adjustments.append("Use simpler words and break long clauses.")

        # If too flat → increase burstiness
        if metrics["lexical_diversity"] < 0.35:
            adjustments.append("Increase lexical variety slightly.")

        guidance = " ".join(adjustments) if adjustments else "Maintain balanced human-like variation."

        base = self.build_prompt(text, t)

        burstiness_block = (
            "\n[BURSTINESS BOOST]\n"
            "Introduce natural variation — mix of short and long sentences, unexpected but meaningful "
            "clause boundaries, human-like pacing shifts, and light cognitive markers like 'well,' "
            "'also,' or 'honestly,'. Avoid robotic parallelism.\n"
        )

        readability_block = (
            f"[READABILITY TARGET]\n{guidance} "
            f"(Flesch target: {ideal['flesch'][0]}–{ideal['flesch'][1]}, "
            f"Coleman-Liau: {ideal['coleman'][0]}–{ideal['coleman'][1]}.)"
        )

        return base + burstiness_block + "\n" + readability_block
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