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
            # "YEAR": re.compile(r"\b(19|20)\d{2}\b"), 
        }
        self._ner_labels = {"PERSON": "NAME", "GPE": "GPE", "LOC": "LOC", "ORG": "ORG"}

    def _get_nlp(self):
        if self._nlp is None:
            try:
                self._nlp = spacy.load("en_core_web_sm")
            except OSError:
                raise RuntimeError("Run: python -m spacy download en_core_web_sm before using this service.")
        return self._nlp

    def mask_pii(self, text: str, strategy: str = "placeholder") -> Tuple[str, Dict[str, str]]:
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

    def restore_pii(self, masked_text: str, restore_map: Dict[str, str]) -> str:
        if not masked_text or not restore_map:
            return masked_text

        restored = masked_text

        # Handle HASH tokens flexibly (Gemini rewrites them unpredictably)
        hash_pattern = re.compile(
            r"\[\[\s*hash\s*:\s*([A-Fa-f0-9]{8,64})\s*\]\]",
            re.IGNORECASE
        )

        def hash_replacer(match):
            key = match.group(1).strip().lower()

            # find original text by matching hash substring
            for placeholder, original in restore_map.items():
                if "HASH:" in placeholder:
                    ph_key = placeholder.split("HASH:")[1].rstrip("]]").lower()
                    if ph_key == key:
                        return original
            return match.group(0)  # fallback

        restored = hash_pattern.sub(hash_replacer, restored)

        # Restore placeholder-based tokens e.g. [[NAME_1]]
        for placeholder, original in sorted(restore_map.items(), key=lambda x: len(x[0]), reverse=True):
            cleaned_ph = re.escape(placeholder)
            restored = re.sub(cleaned_ph, original, restored, flags=re.IGNORECASE)

        return restored


# # Example usage
# if __name__ == "__main__":
#     service = PiiService()
#     text = " Norse mythology is the body of myths from the North Germanic peoples, particularly the Scandinavians during the Viking Age, that was based on Old Norse religion and passed down through oral tradition and later in medieval texts. It features a complex cosmology with nine worlds supported by the world tree Yggdrasil, and a pantheon of gods and goddesses from tribes like the Aesir and Vanir, with prominent figures including Odin, Thor, and Loki."
#     masked, mapping = service.mask_pii(text)
#     print("Masked:\n", masked)
#     print("\nMapping:\n", mapping)
#     restored = service.restore_pii(masked, mapping)
#     print("\nRestored:\n", restored)
