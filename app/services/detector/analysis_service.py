# import math
# import re
# from collections import Counter
# import nltk
# import textstat
# import spacy

# nlp = spacy.load("en_core_web_sm")

# class TextAnalysisService:

#     # ---------- 1. CLEAN TEXT ----------
#     def clean(self, text: str):
#         text = text.lower()
#         text = re.sub(r"[^a-zA-Z0-9\s.?!]", "", text)
#         return text

#     # ---------- 2. PSEUDO-PERPLEXITY ----------
#     def compute_perplexity(self, text: str):
#         text = self.clean(text)
#         words = text.split()

#         if len(words) < 3:
#             return 0.0  # Not enough text

#         unigram_counts = Counter(words)
#         total_words = sum(unigram_counts.values())

#         probabilities = [
#             unigram_counts[word] / total_words for word in words
#         ]

#         log_probs = [math.log2(p) for p in probabilities if p > 0]

#         if not log_probs:
#             return 0.0

#         avg_log_prob = sum(log_probs) / len(log_probs)
#         perplexity = 2 ** (-avg_log_prob)

#         return round(perplexity, 2)

#     # ---------- 3. STYLOMETRIC FEATURES ----------
#     def compute_stylometric_features(self, text: str):
#         doc = nlp(text)

#         sentences = list(doc.sents)
#         num_sentences = len(sentences)
#         words = [token.text for token in doc if token.is_alpha]
#         num_words = len(words)

#         # Avoid division error
#         if num_sentences == 0 or num_words == 0:
#             return {}

#         avg_sentence_length = num_words / num_sentences
#         vocab_richness = len(set(words)) / num_words
#         punctuation_count = sum(1 for token in doc if token.is_punct)

#         # Burstiness = variance of sentence lengths
#         sentence_lengths = [len(sentence) for sentence in sentences]
#         burstiness = (max(sentence_lengths) - min(sentence_lengths)) if len(sentence_lengths) > 1 else 0

#         readability_score = textstat.flesch_reading_ease(text)

#         return {
#             "avg_sentence_length": round(avg_sentence_length, 2),
#             "vocab_richness": round(vocab_richness, 2),
#             "punctuation_count": punctuation_count,
#             "burstiness": burstiness,
#             "readability_score": readability_score
#         }

#     # ---------- 4. FULL ANALYSIS ----------
#     def analyze(self, text: str):
#         return {
#             "perplexity": self.compute_perplexity(text),
#             "stylometry": self.compute_stylometric_features(text)
#         }




import nltk
import textstat
from typing import List, Dict, Any
from nltk.tokenize import sent_tokenize
import nltk
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)


class TextAnalysisService:

    def analyze_sentence(self, sentence: str) -> Dict[str, Any]:
        """Compute perplexity + stylometry for a single sentence."""

        words = sentence.split()

        # Dummy perplexity baseline (replace with GPT-2 or RWKV later)
        perplexity = max(10.0, 80.0 - len(words))  # simple curve

        # Stylometry features
        avg_sentence_length = len(words)
        unique_words = len(set(words)) if words else 1
        vocab_richness = unique_words / max(1, len(words))
        punctuation_count = sum(1 for c in sentence if c in ",.!?;:")
        burstiness = abs(avg_sentence_length - 20)  # rough
        readability = textstat.flesch_reading_ease(sentence)

        return {
            "perplexity": perplexity,
            "stylometry": {
                "avg_sentence_length": avg_sentence_length,
                "vocab_richness": round(vocab_richness, 3),
                "punctuation_count": punctuation_count,
                "burstiness": burstiness,
                "readability_score": readability
            }
        }

    def analyze_text(self, text: str) -> List[Dict[str, Any]]:
        """Return sentence-level analysis list."""
        sentences = sent_tokenize(text)

        results = []
        for s in sentences:
            clean_s = s.strip()
            if not clean_s:
                continue

            data = self.analyze_sentence(clean_s)
            data["sentence"] = clean_s
            results.append(data)

        return results
