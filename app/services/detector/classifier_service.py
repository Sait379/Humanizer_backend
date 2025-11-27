# from functools import lru_cache
# from typing import List
# from transformers import pipeline
# import nltk

# # Ensure tokenizer downloads
# nltk.download('punkt', quiet=True)

# MODEL_NAME = "fakespot-ai/roberta-base-ai-text-detection-v1"


# def _interpret_label_as_ai_prob(label: str, score: float) -> float:
#     """Interpret model prediction as probability text is AI-generated."""
#     label_lower = label.lower()

#     if "ai" in label_lower or "machine" in label_lower or "generated" in label_lower:
#         return float(score)

#     if "human" in label_lower:
#         return float(1.0 - score)

#     if label_lower in ("label_1", "1"):
#         return float(score)

#     if label_lower in ("label_0", "0"):
#         return float(1.0 - score)

#     return 0.5


# class ClassifierService:
#     """AI text detector with automatic chunking (400-token chunks)."""

#     def __init__(self):
#         self._classifier = self._get_pipeline()

#     @staticmethod
#     @lru_cache(maxsize=1)
#     def _get_pipeline():
#         return pipeline(
#             task="text-classification",
#             model=MODEL_NAME,
#             device=-1  # CPU
#         )

#     # ----------------------------
#     # CHUNKING IMPLEMENTATION
#     # ----------------------------
#     def _split_into_chunks(self, text: str, max_tokens: int = 400) -> List[str]:
#         """Split a long text into chunks safe for RoBERTa (limit 512)."""
#         words = text.split()
#         chunks = []

#         for i in range(0, len(words), max_tokens):
#             chunk = " ".join(words[i:i + max_tokens])
#             chunks.append(chunk)

#         return chunks
#     def predict_sentence(self, sentence: str) -> float:
#         """Predict AI probability for a single sentence."""
#         if not sentence.strip():
#             return 0.5

#         try:
#             result = self._classifier(sentence)[0]
#             label = result.get("label", "")
#             score = result.get("score", 0.5)
#             return _interpret_label_as_ai_prob(label, score)
#         except Exception:
#             return 0.5


#     def predict_ai_probability(self, text: str) -> float:
#         """Run classifier on each chunk and return average AI probability."""
#         if not text or len(text.split()) < 5:
#             return 0.5

#         # Split text into safe chunks
#         chunks = self._split_into_chunks(text)

#         ai_probs = []

#         for chunk in chunks:
#             try:
#                 result = self._classifier(chunk)[0]
#                 label = result.get("label", "")
#                 score = result.get("score", 0.5)

#                 ai_prob = _interpret_label_as_ai_prob(label, score)
#                 ai_probs.append(ai_prob)

#             except Exception:
#                 ai_probs.append(0.5)

#         # Average over all chunks
#         final_score = sum(ai_probs) / len(ai_probs)
#         return round(final_score, 4)







# from functools import lru_cache
# from typing import List
# from transformers import pipeline
# import nltk

# # Download tokenizer data
# nltk.download("punkt", quiet=True)

# MODEL_NAME = "Hello-SimpleAI/chatgpt-detector-roberta"


# def _interpret_label_as_ai_prob(label: str, score: float) -> float:
#     """
#     Convert model's output to "probability text is AI".
#     Supports multiple label styles:
#     - AI / Human
#     - LABEL_0 / LABEL_1
#     """

#     label = label.lower()

#     # Many detectors use "AI" vs "Human"
#     if "ai" in label or "generated" in label:
#         return float(score)

#     if "human" in label:
#         return float(1.0 - score)

#     # Some models use binary labels
#     if label in ("label_1", "1"):
#         return float(score)

#     if label in ("label_0", "0"):
#         return float(1.0 - score)

#     # If unknown, fall back to neutral
#     return 0.5


# class ClassifierService:
#     """AI text detector with automatic chunking."""

#     def __init__(self):
#         self._classifier = self._get_pipeline()

#     @staticmethod
#     @lru_cache(maxsize=1)
#     def _get_pipeline():
#         return pipeline(
#             task="text-classification",
#             model=MODEL_NAME,
#             device=-1,  # CPU
#             truncation=True
#         )

#     # ----------------------------
#     # CHUNKING IMPLEMENTATION
#     # ----------------------------
#     def _split_into_chunks(self, text: str, max_tokens: int = 400) -> List[str]:
#         """Split into approx. 400-token chunks (safe for RoBERTa)."""
#         words = text.split()
#         chunks = []

#         for i in range(0, len(words), max_tokens):
#             chunk = " ".join(words[i:i + max_tokens])
#             chunks.append(chunk)

#         return chunks
#     def predict_sentence(self, sentence: str) -> float:
#         """Predict AI probability for a single sentence."""
#         if not sentence.strip():
#             return 0.5

#         try:
#             result = self._classifier(sentence)[0]
#             label = result.get("label", "")
#             score = result.get("score", 0.5)
#             return _interpret_label_as_ai_prob(label, score)
#         except Exception:
#             return 0.5


#     # ----------------------------
#     # MAIN PREDICT FUNCTION
#     # ----------------------------
#     def predict_ai_probability(self, text: str) -> float:
#         """Run detector on each chunk and average results."""

#         if not text or len(text.split()) < 5:
#             return 0.5

#         chunks = self._split_into_chunks(text)
#         ai_probs = []

#         for chunk in chunks:
#             try:
#                 result = self._classifier(chunk)[0]
#                 label = result.get("label", "")
#                 score = result.get("score", 0.5)

#                 ai_prob = _interpret_label_as_ai_prob(label, score)
#                 ai_probs.append(ai_prob)

#             except Exception:
#                 ai_probs.append(0.5)

#         final_score = sum(ai_probs) / len(ai_probs)
#         return round(final_score, 4)



from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
import torch

MODEL_NAME = "openai-community/roberta-large-openai-detector"

class ClassifierService:
    """
    Loads the OpenAI-community RoBERTa detector and predicts AI probability.
    """

    def __init__(self):
        self._classifier = self._get_pipeline()

    def _get_pipeline(self):
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

        return TextClassificationPipeline(
            model=model,
            tokenizer=tokenizer,
            device=0 if torch.cuda.is_available() else -1,
            top_k=None
        )

    def predict_proba(self, text: str) -> float:
        """
        Returns AI probability (0–1) using:
        LABEL_1 → AI
        LABEL_0 → Human
        """

        output = self._classifier(text)

        # output = [[{label, score}, {label, score}]]
        preds = output[0]  # first list

        # Find LABEL_1 (AI)
        ai_score = None
        human_score = None

        for item in preds:
            if item["label"] == "LABEL_1":
                ai_score = float(item["score"])
            elif item["label"] == "LABEL_0":
                human_score = float(item["score"])

        # final fallback
        if ai_score is not None:
            return ai_score
        if human_score is not None:
            return 1 - human_score

        # Should never happen
        return 0.5
 # convert human → AI probability

    # required for your line-by-line detection
    def predict_sentence(self, sentence: str) -> float:
        return self.predict_proba(sentence)

