# from app.services.detector.analysis_service import TextAnalysisService
# from app.services.detector.classifier_service import ClassifierService
# from app.services.detector.ensemble_service import EnsembleService


# class DetectorService:
#     def __init__(self):
#         self.analysis_service = TextAnalysisService()
#         self.classifier_service = ClassifierService()
#         self.ensemble_service = EnsembleService()

#     def analyze(self, text: str):
#         # 1) Perplexity + stylometry
#         analysis = self.analysis_service.analyze(text)
#         perplexity = analysis.get("perplexity", 0.0)
#         stylometry = analysis.get("stylometry", {})

#         # 2) Classifier AI probability
#         ai_prob = self.classifier_service.predict_ai_probability(text)

#         # 3) Ensemble AI score (0–100)
#         ai_score = self.ensemble_service.compute_ai_score(
#     perplexity=perplexity,
#     stylometry=stylometry,
#     classifier_ai_prob=ai_prob,
#     text=text
# )


#         # OPTION C: Simple final score output
#         return {
#             "ai_score": ai_score,
#             # If you ALSO want debug info, keep this; otherwise you can remove.
#             "meta": {
#                 "perplexity": perplexity,
#                 "stylometry": stylometry,
#                 "classifier_ai_probability": ai_prob
#             }
#         }


from app.services.detector.classifier_service import ClassifierService
import nltk
from nltk.tokenize import sent_tokenize

# ensure tokenizer
nltk.download("punkt", quiet=True)


class DetectorService:

    def __init__(self):
        self.classifier = ClassifierService()

    def analyze(self, text: str):

        # Split into sentences
        sentences = sent_tokenize(text)

        if not sentences:
            return {"ai_score": 50.0}

        probs = []

        for sentence in sentences:
            if sentence.strip():
                prob = self.classifier.predict_sentence(sentence)
                probs.append(prob)

        if not probs:
            return {"ai_score": 50.0}

        # average classifier probabilities
        avg_prob = sum(probs) / len(probs)

        return {
            "ai_score": round(avg_prob * 100, 2)
        }
