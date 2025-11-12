# services/common/scoring_service.py
import textstat

class ScoringService:
    """
    Provides readability and linguistic quality scoring for both 
    preprocessed (normalized) and postprocessed (humanized) text.
    Assumes text is already cleaned and normalized.
    """

    def __init__(self):
        pass

    def _evaluate(self, text: str) -> dict:
        """
        Core scoring logic — calculates readability and lexical metrics.
        Includes Gunning Fog Index (GFI) for sentence complexity.
        """
        if not text or not isinstance(text, str) or len(text.strip()) == 0:
            return {
                "flesch_reading_ease": 0,
                "grade_level": 0,
                "smog_index": 0,
                "coleman_liau_index": 0,
                "gunning_fog_index": 0,
                "lexical_diversity": 0,
                "word_count": 0,
                "overall_score": 0,
            }

        # --- Readability Metrics ---
        flesch = textstat.flesch_reading_ease(text)
        grade = textstat.flesch_kincaid_grade(text)
        smog = textstat.smog_index(text)
        coleman = textstat.coleman_liau_index(text)
        gfi = textstat.gunning_fog(text)   # ✅ Added Gunning Fog Index

        # --- Lexical Statistics ---
        words = text.split()
        word_count = len(words)
        unique_words = len(set(words))
        lexical_diversity = round(unique_words / word_count, 3) if word_count else 0

        # --- Overall Combined Score (0–100 scale) ---
        # Weigh Flesch (clarity) + GFI (complexity inverse) + lexical diversity
        # Lower GFI → better readability, so we invert it slightly
        gfi_adjusted = max(0, min(100, 100 - (gfi * 5)))  # Scaled inversely
        overall_score = round(
            (flesch * 0.5) + (gfi_adjusted * 0.2) + (lexical_diversity * 100 * 0.3), 2
        )

        return {
            "flesch_reading_ease": round(flesch, 2),
            "grade_level": round(grade, 2),
            "smog_index": round(smog, 2),
            "coleman_liau_index": round(coleman, 2),
            "gunning_fog_index": round(gfi, 2),
            "lexical_diversity": lexical_diversity,
            "word_count": word_count,
            "overall_score": overall_score,
        }

    def evaluate_preprocessed_text(self, text: str) -> dict:
        """
        Evaluate baseline score for preprocessed (normalized) text.
        Used before humanization.
        """
        score = self._evaluate(text)
        score["stage"] = "preprocessed"
        return score

    def evaluate_postprocessed_text(self, text: str) -> dict:
        """
        Evaluate final score for postprocessed (humanized) text.
        Used after grammar correction and PII restoration.
        """
        score = self._evaluate(text)
        score["stage"] = "postprocessed"
        return score

    def compare_scores(self, pre: dict, post: dict) -> dict:
        """
        Compare readability improvements between pre and post scores.
        Returns delta for each numeric metric along with quality tag.
        """
        if not pre or not post:
            return {}

        delta = {}
        for key, pre_value in pre.items():
            if key in post and isinstance(pre_value, (int, float)):
                delta[key] = round(post[key] - pre_value, 2)

        # Add a qualitative summary
        if "overall_score" in delta:
            if delta["overall_score"] > 5:
                delta["quality_status"] = "Improved"
            elif delta["overall_score"] < -5:
                delta["quality_status"] = "Declined"
            else:
                delta["quality_status"] = "Stable"

        return delta

if __name__ == "__main__":
    # ✅ Manual testing block
    service = ScoringService()

    # Example input texts
    pre_text = "The utilization of advanced computational methodologies improves operational efficiency."
    post_text = "Using better computer methods makes work faster."

    # Evaluate both
    pre_score = service.evaluate_preprocessed_text(pre_text)
    post_score = service.evaluate_postprocessed_text(post_text)
    comparison = service.compare_scores(pre_score, post_score)

    # Print outputs
    print("\n--- Preprocessed Text Score ---")
    print(pre_score)

    print("\n--- Postprocessed Text Score ---")
    print(post_score)

    print("\n--- Improvement Comparison ---")
    print(comparison)
