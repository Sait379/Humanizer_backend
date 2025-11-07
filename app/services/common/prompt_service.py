from typing import Optional


class PromptService:
    """
    Builds dynamic, highly-constrained, and tone-aware prompts optimized for 
    Gemini. Each prompt includes a single-shot demonstration for in-context learning.
    """

    DEMO_INPUT = "The company has informed its personnel that a new directive related to workflow optimization will commence on Monday."

    PROMPTS = {
        "neutral": (
            "[INSTRUCTION] You are an expert human editor. The following text has already been cleaned and normalized. "
            "Your task is to humanize it — make it sound natural, fluid, and genuinely human-written — while keeping the tone neutral "
            "and the meaning fully intact. Do NOT remove punctuation or fix grammar unless absolutely needed. "
            "Focus on improving flow, phrasing, and rhythm so it reads as if written by a real person, not an AI.\n\n"
            "--- DEMONSTRATION ---\n"
            "Input: The utilization of advanced computational methodologies improves operational efficiency.\n"
            "Output: Using advanced computing methods makes work more efficient.\n"
            "--- END DEMONSTRATION ---\n\n"
            "Text to humanize:\n{text}"
        ),
        "friendly": (
            "[INSTRUCTION] Assume the persona of a Warm and Approachable Colleague. Rephrase the input text to adopt a naturally conversational, optimistic, and welcoming tone. "
            "Constraint: Use contractions and prioritize positive language.\n\n"
            "--- DEMONSTRATION ---\n"
            f"Input: {DEMO_INPUT}\n"
            "Output: Hey team, just letting everyone know we're kicking off a new way to optimize our work processes starting Monday!\n"
            "--- END DEMONSTRATION ---\n\n"
            "Input Text:\n{text}"
        ),
        "formal": (
            "[INSTRUCTION] Assume the role of a Senior Academic Editor. Render the following text using a precise, formal, and highly polished register, suitable for official or scholarly documents. "
            "Constraint: STRICTLY avoid all colloquialisms, slang, and contractions. Maintain elevated, grammatically precise language.\n\n"
            "--- DEMONSTRATION ---\n"
            f"Input: {DEMO_INPUT}\n"
            "Output: The organization has notified its employees that a formal directive concerning workflow optimization will be implemented on Monday.\n"
            "--- END DEMONSTRATION ---\n\n"
            "Input Text:\n{text}"
        ),
        "professional": (
            "[INSTRUCTION] Act as a Corporate Communications Specialist. Rewrite the text to reflect a confident, results-oriented, and business-appropriate voice. "
            "Constraint: The output MUST be concise, prioritize clarity over length, and focus on objective outcomes without losing the original meaning.\n\n"
            "--- DEMONSTRATION ---\n"
            f"Input: {DEMO_INPUT}\n"
            "Output: A new workflow optimization policy will be implemented for all personnel starting Monday.\n"
            "--- END DEMONSTRATION ---\n\n"
            "Input Text:\n{text}"
        ),
        "casual": (
            "[INSTRUCTION] Adopt the style of an everyday, relaxed message to a close friend. Rewrite the text to be extremely casual, breezy, and brief. "
            "Constraint: Use short, punchy sentences. Emotional or enthusiastic language is encouraged.\n\n"
            "--- DEMONSTRATION ---\n"
            f"Input: {DEMO_INPUT}\n"
            "Output: Heads up: the company is changing how we work starting Monday to make things smoother.\n"
            "--- END DEMONSTRATION ---\n\n"
            "Input Text:\n{text}"
        ),
        "empathetic": (
            "[INSTRUCTION] Act as a Compassionate Listener focused on supportive communication. Rewrite the text to incorporate genuine warmth, understanding, and validation. "
            "Constraint: The language MUST prioritize emotional connection and gentleness, acknowledging potential recipient feelings without changing the factual basis.\n\n"
            "--- DEMONSTRATION ---\n"
            f"Input: {DEMO_INPUT}\n"
            "Output: We understand that changes to your workflow can be a lot. Please know that a new optimization process will begin Monday, and we are here to support you through the transition.\n"
            "--- END DEMONSTRATION ---\n\n"
            "Input Text:\n{text}"
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