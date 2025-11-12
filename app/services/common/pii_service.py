"""
pii_service.py — Utility module for Hybrid PII detection/masking (no separate FastAPI router)

Used internally in /humanize pipeline:
    masked_text, pii_map = self.pii_service.mask_pii(text)
    restored_text = self.pii_service.restore_pii(humanized_text, pii_map)

✅ Uses spaCy NER for unstructured PII (names, locations, orgs)
✅ Uses regex for structured identifiers (email, phone, PAN, Aadhaar, IFSC, IPv4)
✅ Returns reversible mapping for restoration after LLM rewrite

Dependencies:
    pip install spacy
    python -m spacy download en_core_web_sm
"""

import re
import hashlib
import spacy
from typing import Dict, Tuple, List

class PiiService:
    def __init__(self):
        self._nlp = None
        self._patterns = {
            "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            "PHONE": re.compile(r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)"),
            "PAN": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
            "AADHAAR": re.compile(r"(?<!\d)(?:\d{4}\s?\d{4}\s?\d{4})(?!\d)"),
            "IFSC": re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b"),
            "IPV4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        }
        self._ner_labels = {"PERSON": "NAME", "GPE": "GPE", "LOC": "LOC", "ORG": "ORG"}

    def _get_nlp(self):
        if self._nlp is None:
            try:
                self._nlp = spacy.load("en_core_web_sm")
            except OSError:
                raise RuntimeError("Run: python -m spacy download en_core_web_sm before using this service.")
        return self._nlp

    def mask_pii(self, text: str, strategy: str = "hash") -> Tuple[str, Dict[str, str]]:
        if not text:
            return text, {}

        nlp = self._get_nlp()
        doc = nlp(text)
        spans: List[Tuple[int, int, str, str]] = []  # start, end, label, value

        # Regex matches
        for label, pattern in self._patterns.items():
            for m in pattern.finditer(text):
                spans.append((m.start(), m.end(), label, m.group(0)))

        # NER matches
        for ent in doc.ents:
            if ent.label_ in self._ner_labels:
                mapped_label = self._ner_labels[ent.label_]
                spans.append((ent.start_char, ent.end_char, mapped_label, ent.text))

        # Sort by start
        spans.sort(key=lambda s: s[0])

        masked_text = text
        restore_map: Dict[str, str] = {}
        offset = 0
        label_count: Dict[str, int] = {}

        for start, end, label, value in spans:
            label_count[label] = label_count.get(label, 0) + 1
            idx = label_count[label]

            if strategy == "placeholder":
                placeholder = f"[[{label}_{idx}]]"
            elif strategy == "redact":
                placeholder = "█" * len(value)
            elif strategy == "hash":
                placeholder = f"[[HASH:{hashlib.sha256(value.encode()).hexdigest()[:10]}]]"
            else:
                placeholder = f"[[{label}_{idx}]]"

            restore_map[placeholder] = value
            masked_text = masked_text[: start + offset] + placeholder + masked_text[end + offset :]
            offset += len(placeholder) - (end - start)

        return masked_text, restore_map

    # def restore_pii(self, masked_text: str, restore_map: Dict[str, str]) -> str:
    #     if not masked_text or not restore_map:
    #         return masked_text
    #     restored = masked_text
    #     # Replace longer placeholders first
    #     for placeholder, original in sorted(restore_map.items(), key=lambda x: len(x[0]), reverse=True):
    #         restored = restored.replace(placeholder, original)
    #     return restored

# Example usage
if __name__ == "__main__":
    service = PiiService()
    text = "Ayushi Gupta lives in Delhi. Email: ayushi@example.com, PHONE: +91-9876543210, PAN: ABCDE1234F."
    masked, mapping = service.mask_pii(text)
    print("Masked:\n", masked)
    print("\nMapping:\n", mapping)
    # restored = service.restore_pii(masked, mapping)
    # print("\nRestored:\n", restored)
