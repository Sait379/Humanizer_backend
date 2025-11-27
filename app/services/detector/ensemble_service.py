# # from typing import Dict, Any


# # class EnsembleService:
# #     """
# #     Combines:
# #       - perplexity
# #       - stylometric features
# #       - classifier AI probability
# #     into a single AI-likelihood score (0–100).
# #     """

# #     def _normalize_perplexity(self, perplexity: float) -> float:
# #         """
# #         Map perplexity to human-likeness in [0, 1].
# #         Lower perplexity => more AI-like.
# #         """
# #         if perplexity <= 25:
# #             return 0.0
# #         if perplexity >= 60:
# #             return 1.0
# #         return (perplexity - 25) / (60 - 25)

# #     def _normalize_burstiness(self, burstiness: float) -> float:
# #         """
# #         Burstiness = variation in sentence length.
# #         Low burstiness => AI-like, higher => human-like (up to a point).
# #         """
# #         if burstiness <= 3:
# #             return 0.0
# #         if burstiness >= 12:
# #             return 1.0
# #         return (burstiness - 3) / (12 - 3)

# #     def _normalize_vocab_richness(self, vocab_richness: float) -> float:
# #         """
# #         Higher lexical diversity tends to be human-like.
# #         Clamp between ~0.65 (AI-ish) and 1.0 (human-like).
# #         """
# #         return max(0.0, min(1.0, (vocab_richness - 0.65) / (1.0 - 0.65)))

# #     def _normalize_avg_sentence_length(self, avg_sentence_length: float) -> float:
# #         """
# #         Penalize extremes. Humans often cluster around 15–25 words/sentence.
# #         """
# #         if avg_sentence_length <= 5 or avg_sentence_length >= 40:
# #             return 0.0
# #         # The closer to 20, the better
# #         return max(0.0, 1.0 - abs(avg_sentence_length - 20.0) / 20.0)

# #     def _normalize_readability(self, readability_score: float) -> float:
# #         """
# #         Flesch Reading Ease: 0–100 (can be negative or >100).
# #         Medium range (~30–70) is most human-like.
# #         Very high or very low can be AI-ish.
# #         """
# #         # Clamp rough range for safety
# #         if readability_score < 0:
# #             readability_score = 0
# #         if readability_score > 100:
# #             readability_score = 100

# #         # Map 0–100 such that 30–70 is "good"
# #         if readability_score < 30 or readability_score > 70:
# #             return 0.3
# #         return 0.8

# #     def compute_ai_score(
# #         self,
# #         perplexity: float,
# #         stylometry: Dict[str, Any],
# #         classifier_ai_prob: float
# #     ) -> float:
# #         """
# #         Returns final AI score (0–100).
# #         """

# #         avg_sentence_length = stylometry.get("avg_sentence_length", 0.0)
# #         vocab_richness = stylometry.get("vocab_richness", 0.0)
# #         burstiness = stylometry.get("burstiness", 0.0)
# #         readability_score = stylometry.get("readability_score", 50.0)

# #         # 1) Convert to human-likeness scores (0–1)
# #         perplexity_human = self._normalize_perplexity(perplexity)
# #         burstiness_human = self._normalize_burstiness(burstiness)
# #         vocab_human = self._normalize_vocab_richness(vocab_richness)
# #         avg_len_human = self._normalize_avg_sentence_length(avg_sentence_length)
# #         readability_human = self._normalize_readability(readability_score)

# #         # 2) Classifier gives AI-likeness directly (0–1)
# #         classifier_ai = max(0.0, min(1.0, classifier_ai_prob))
# #         classifier_human = 1.0 - classifier_ai

# #         # 3) Weighted human-likeness from all signals
# #         # You can tweak these weights later
# #         human_score = (
# #             perplexity_human * 0.30 +
# #             burstiness_human * 0.20 +
# #             vocab_human * 0.15 +
# #             avg_len_human * 0.10 +
# #             readability_human * 0.05 +
# #             classifier_human * 0.20
# #         )

# #         # Clamp to [0, 1]
# #         human_score = max(0.0, min(1.0, human_score))

# #         # 4) Convert to AI% (0–100)
# #         ai_score = (1.0 - human_score) * 100.0
# #         return round(ai_score, 2)


# from typing import Dict, Any


# class EnsembleService:
#     """
#     Calibrates classifier output using stylometry + perplexity.
#     Returns final AI score (0–100) after correction.
#     """

#     def compute_ai_score(
#         self,
#         perplexity: float,
#         stylometry: Dict[str, Any],
#         classifier_ai_prob: float,
#         text: str = ""
#     ) -> float:

#         score = max(0.0, min(1.0, classifier_ai_prob))  # base value 0–1

#         # ------------------------
#         # 1) SHORT TEXT CORRECTION
#         # ------------------------
#         if text and len(text) < 200:
#             score *= 0.75  # reduce false positives

#         # ------------------------
#         # 2) REPETITION CORRECTION
#         # ------------------------
#         if text:
#             words = text.split()
#             total_words = len(words)
#             unique_words = len(set(words))
#             uniqueness = unique_words / total_words if total_words > 0 else 1
#             score *= (0.80 + uniqueness * 0.20)  # repetitive → AI, unique → human

#         # ------------------------
#         # 3) PUNCTUATION CORRECTION
#         # ------------------------
#         punctuation_count = stylometry.get("punctuation_count", 0)
#         if punctuation_count == 0:
#             score *= 0.85  # humans often use punctuation inconsistently

#         # ------------------------
#         # 4) VOCAB RICHNESS CORRECTION
#         # ------------------------
#         vocab_richness = stylometry.get("vocab_richness", 0)
#         if vocab_richness > 0.60:
#             score *= 0.85  # rich vocabulary → more human

#         # ------------------------
#         # 5) BURSTINESS CORRECTION
#         # ------------------------
#         burstiness = stylometry.get("burstiness", 0)
#         if burstiness > 25:
#             score *= 0.80  # sentence variation → human

#         # ------------------------
#         # 6) FINAL SMOOTHING
#         # ------------------------
#         final_score = round(score * 100, 2)
#         final_score = max(0, min(100, final_score))

#         return final_score



from typing import List, Dict, Any

class EnsembleService:

    def score_sentence(self, perplexity, stylometry, classifier_prob, sentence):
        score = classifier_prob

        # Short sentence correction
        if len(sentence) < 50:
            score *= 0.80

        # Repetition correction
        words = sentence.split()
        if words:
            uniqueness = len(set(words)) / len(words)
            score *= (0.70 + uniqueness * 0.30)

        # Punctuation
        if stylometry.get("punctuation_count", 0) == 0:
            score *= 0.85

        # Vocab richness
        if stylometry.get("vocab_richness", 0) > 0.60:
            score *= 0.85

        # Burstiness
        if stylometry.get("burstiness", 0) > 12:
            score *= 0.75

        return max(0, min(1, score))

    def aggregate(self, sentence_scores: List[Dict[str, Any]]) -> float:
        if not sentence_scores:
            return 50.0

        total_weight = 0
        weighted_sum = 0

        for s in sentence_scores:
            sentence = s["sentence"]
            final_prob = s["final_sentence_score"]

            weight = max(1, len(sentence.split()))
            total_weight += weight
            weighted_sum += final_prob * weight

        return round((weighted_sum / total_weight) * 100, 2)
