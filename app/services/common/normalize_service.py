
# services/normalize_service.py
import re, html, emoji, unicodedata, contractions
from textblob import TextBlob
import language_tool_python
# from cleantext import clean

tool = language_tool_python.LanguageTool('en-US')


class NormalizeService:
    """Handles pre-cleaning, masking, normalization, and restoration before LLM processing."""

    # 1️⃣ --- Pre-cleaning ---
    def preclean(self, text: str) -> str:
        """Remove HTML, digits, extra spaces; keep links and emojis."""
        text = html.unescape(re.sub(r'<.*?>', '', text))
        text = unicodedata.normalize("NFKC", text)
        # text = re.sub(r'\d+', '', text)
        text = re.sub(r'([!?.,])\1+', r'\1', text)
        # text = re.sub(r'[\r\n\t]+', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    # 2️⃣ --- Masking of URLs and Emojis ---
    def mask_specials(self, text: str):
        """
        Temporarily mask URLs and emojis so LLM won't alter them.
        Returns masked_text, mapping_dict.
        """
        mapping = {}
        counter = 1

        # Mask URLs
        def url_replacer(match):
            nonlocal counter
            placeholder = f"[URL_{counter}]"
            mapping[placeholder] = match.group(0)
            counter += 1
            return placeholder

        text = re.sub(r'https?://\S+|www\.\S+', url_replacer, text)

        # Mask Emojis
        def emoji_replacer(emoji_char, emoji_data):
            nonlocal counter
            placeholder = f"[EMOJI_{counter}]"
            mapping[placeholder] = emoji_char
            counter += 1
            return placeholder

        text = emoji.replace_emoji(text, replace=emoji_replacer)
        return text, mapping

    # 3️⃣ --- Normalization ---
    def normalize(self, text: str) -> str:
        """Expand contractions, run light cleanup, and leave placeholders untouched."""
        text = contractions.fix(text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'([!?.,])\1+', r'\1', text)
        return text

    # 4️⃣ --- Restoration ---
    def restore(self, text: str, mapping: dict) -> str:
        """Restore masked URLs and emojis back into the text."""
       
        restored_text = text
        # Replace placeholders back with original items
        for placeholder, original in mapping.items():
            restored_text = restored_text.replace(placeholder, original)
        return restored_text

    # 5️⃣ --- Combined Function ---
    def clean_and_normalize(self, text: str) -> dict:
        """Run preclean → mask_specials → normalize → restore."""
        precleaned = self.preclean(text)
        masked_text, mapping = self.mask_specials(precleaned)
        normalized = self.normalize(masked_text)
        restored = self.restore(normalized, mapping)

        return {
            "original_text": text,
            "cleaned_text": normalized,
            "restored_text": restored,
            "mask_map": mapping,
        }


# if __name__ == "__main__":
#     service = NormalizeService()
#     sample_text = """Hey there!! 😄 I dont recently came across this super cant cool article on https://openai.com about AI writing — it’s honestly mind-blowing 🤯!! The way these tools can mimic human creativity is just awesome, though sometimes the tone feels a bit robotic 😅. 
# BTW, if you wanna check some examples, visit www.medium.com or follow my updates on Twitter @ayushi_ai 🤗. 
# Also, I think AI shouldn’t replace writers but empower them to write faster & better 💪!! What do you think??"""

#     result = service.clean_and_normalize(sample_text)

#     print("\n🔹 Original Text:")
#     print(sample_text)
#     print("\n🔹 After Preclean + Mask + Normalize:")
#     print(result["cleaned_text"])
#     print("\n🔹 Restored Text:")
#     print(result["restored_text"])
#     print("\n🔹 Mask Mapping:")
#     print(result["mask_map"])
