# app/services/common/prompt_service.py

from typing import Optional
from app.services.common.scoring_service import ScoringService


class PromptService:
    """
    Builds dynamic, tone-safe, and humanization-optimized prompts
    for use with Gemini on Vertex AI.
    """

    IDEAL_RANGES = {
        "friendly": {"flesch": (75, 100), "coleman": (8, 11)},
        "neutral": {"flesch": (65, 80), "coleman": (9, 12)},
        "formal": {"flesch": (40, 55), "coleman": (12, 15)},
        "professional": {"flesch": (55, 70), "coleman": (10, 13)},
        "casual": {"flesch": (70, 85), "coleman": (8, 11)},
        "empathetic": {"flesch": (65, 80), "coleman": (9, 12)},
    }

    # Placeholder preservation (keep as-is)
    placeholder_rule = """[PLACEHOLDER RULE]
Keep ALL bracketed placeholders exactly as they appear.
Do NOT modify text, characters, spacing, SALT suffixes, or order.
Do NOT replace placeholders with explanations or descriptions.
Return every placeholder unchanged.
"""

    # -------------------
    # UPDATED TONE MAP
    # -------------------
    TONE_MAP = {
        "neutral": (
            "Clear, balanced, human-like writing. Maintain any existing professionalism. "
            "No conversational fillers."
        ),
        "friendly": (
            "Warm and approachable with light, natural human flow. Subtle connectors allowed."
        ),
        "formal": (
            "Refined, structured, human expression without any conversational fillers."
        ),
        "professional": (
            "Concise, confident, steady, and naturally varied — no fillers or overly casual markers."
        ),
        "casual": (
            "Relaxed and conversational. Light connectors allowed, but avoid slang."
        ),
        "empathetic": (
            "Supportive, understanding, and emotionally steady. Light softening connectors allowed."
        ),
    }

    ALLOWED_TONES = set(TONE_MAP.keys())

    # -------------------
    # MAIN HUMANIZATION PROMPT TEMPLATE
    # -------------------
    PROMPTS = {
        "{TONE}": (
            "[HUMANIZATION INSTRUCTION]\n"
            "Rewrite the text so it feels genuinely written by a human, not an AI. Preserve meaning with "
            "absolute precision — no altering facts, intent, or level of formality. Remove AI-like symmetry "
            "or mechanical tone. Increase natural human variation: irregular rhythm, subtle pacing shifts, "
            "mixed sentence lengths, and mild lexical variety.\n\n"

            "[HUMAN CADENCE]\n"
            "Use natural pacing through varied sentence lengths and gentle rhythm changes. Do NOT introduce "
            "conversational fillers such as 'well,' 'honestly,' 'to be fair,' or similar phrases in formal, "
            "professional, or neutral contexts. Maintain organic flow without robotic balance.\n\n"

            "[FORMALITY CHECK]\n"
            "If the text appears formal, academic, or professional in nature, preserve that style fully "
            "and avoid any informal markers regardless of the selected tone.\n\n"

            "[SAFETY & PRESERVATION]\n"
            "Do not change numbers, dates, IDs, URLs, bullet structure, markdown, or emojis. Keep ALL formatting "
            "unchanged: spacing, new lines, lists, symbols. No added commentary or explanations.\n\n"

            "{PLACEHOLDER_RULE}\n\n"

            "[TONE]\n"
            "{TONE_SPECIFIC}\n\n"

            "[TEXT TO REWRITE]\n"
            "{text}\n\n"

            "[OUTPUT CONSTRAINT]\n"
            "Return ONLY the rewritten text with identical formatting and placeholders."
        )
    }

    def __init__(self, tone: Optional[str] = None):
        self.tone = tone.lower().strip() if tone else "neutral"
        if self.tone not in self.ALLOWED_TONES:
            print(f"Warning: Tone '{self.tone}' not supported. Defaulting to 'neutral'.")
            self.tone = "neutral"

    # -------------------
    # BASE PROMPT BUILDER
    # -------------------
    def build_prompt(self, text, tone: Optional[str] = None) -> str:
        if isinstance(text, list):
            text = " ".join(map(str, text))

        t = (tone or self.tone).lower().strip()
        if t not in self.ALLOWED_TONES:
            t = "neutral"

        tone_specific = self.TONE_MAP.get(t, self.TONE_MAP["neutral"])

        base_template = self.PROMPTS["{TONE}"]
        prompt = (
            base_template
            .replace("{TONE_SPECIFIC}", tone_specific)
            .replace("{TONE}", t)
            .replace("{PLACEHOLDER_RULE}", self.placeholder_rule)
            .format(text=str(text).strip())
        )
        return prompt

    # -------------------
    # DYNAMIC PROMPT BUILDER (Burstiness + Readability)
    # -------------------
    def build_dynamic_prompt(self, text: str, tone: str) -> str:
        scoring_service = ScoringService()
        metrics = scoring_service.evaluate_preprocessed_text(text)

        t = tone.lower().strip() if tone else "neutral"
        if t not in self.ALLOWED_TONES:
            t = "neutral"

        ideal = self.IDEAL_RANGES[t]
        adjustments = []

        # Too simple → increase richness
        if metrics["flesch_reading_ease"] > ideal["flesch"][1]:
            adjustments.append("Introduce slightly richer phrasing and some longer sentences.")

        # Too complex → simplify
        if metrics["coleman_liau_index"] > ideal["coleman"][1]:
            adjustments.append("Simplify word choice and split long clauses if needed.")

        # Too flat → boost lexical diversity
        if metrics["lexical_diversity"] < 0.35:
            adjustments.append("Increase lexical variety in a subtle, human way.")

        guidance = (
            " ".join(adjustments)
            if adjustments
            else "Maintain balanced, natural human-like variation."
        )

        base = self.build_prompt(text, t)

        burstiness_block = (
            "\n[BURSTINESS BOOST]\n"
            "Use natural irregularity: occasional reflective longer sentences mixed with shorter lines. "
            "Keep rhythm human but not chaotic. No conversational fillers in formal or professional content.\n"
        )

        readability_block = (
            f"[READABILITY TARGET]\n"
            f"{guidance} (Flesch: {ideal['flesch'][0]}–{ideal['flesch'][1]}, "
            f"Coleman-Liau: {ideal['coleman'][0]}–{ideal['coleman'][1]}.)"
        )

        return base + burstiness_block + "\n" + readability_block
    
    @staticmethod
    def paraphrase_prompt(text: str) -> str:
        return (
            "Paraphrase the given text.\n"
            "Do NOT change its meaning.\n"
            "Do NOT expand or explain anything.\n"
            "Return a single rewritten version only.\n"
            "Output only the paraphrased sentence.\n\n"
            f"{text}"
        )