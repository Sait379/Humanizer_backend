# # services/normalize_service.py
# import re, html, emoji, unicodedata, contractions

# class NormalizeService:
#     """Handles pre-cleaning, masking, and normalization before LLM processing."""
    
#     def __init__(self):
#         # Use UNIQUE invisible Unicode characters for different types
#         self.EMOJI_MARKER = '\u200B'  # Zero-width space (for emojis)
#         self.URL_MARKER = '\u200C'    # Zero-width non-joiner (for URLs)
    
#     # 1️⃣ --- Pre-cleaning ---
#     def preclean(self, text: str) -> str:
#         """Remove HTML, digits, extra spaces; keep links and emojis."""
#         text = html.unescape(re.sub(r'<.*?>', '', text))
#         text = unicodedata.normalize("NFKC", text)
#         # text = re.sub(r'\d+', '', text)
#         text = re.sub(r'([!?.,])\1+', r'\1', text)
#         text = re.sub(r'[\r\n\t]+', ' ', text)
#         text = re.sub(r'\s+', ' ', text).strip()
#         return text
    
#     # 2️⃣ --- Masking of URLs and Emojis ---
#     def mask_specials(self, text: str):
#         """
#         Temporarily mask URLs and emoji SEQUENCES using invisible markers.
#         Returns masked_text and ordered list of replacements.
#         """
#         replacements = []  # Ordered list: [(marker_type, original_content), ...]
        
#         # Mask URLs first
#         def url_replacer(match):
#             original = match.group(0)
#             replacements.append(('url', original))
#             return self.URL_MARKER
        
#         text = re.sub(r'https?://\S+|www\.\S+', url_replacer, text)
        
#         # Extract all emojis with positions
#         emoji_data = emoji.emoji_list(text)
        
#         if not emoji_data:
#             return text, replacements
        
#         # Build masked text by grouping consecutive IDENTICAL emojis
#         result = []
#         last_end = 0
#         i = 0
        
#         while i < len(emoji_data):
#             current = emoji_data[i]
#             start_pos = current['match_start']
#             current_emoji = current['emoji']
            
#             # Add text before this emoji/group
#             result.append(text[last_end:start_pos])
            
#             # Collect consecutive identical emojis (with optional whitespace)
#             emoji_sequence = current_emoji
#             end_pos = current['match_end']
            
#             # Look ahead for identical emojis
#             while i + 1 < len(emoji_data):
#                 next_emoji_data = emoji_data[i + 1]
#                 next_emoji = next_emoji_data['emoji']
#                 between_text = text[end_pos:next_emoji_data['match_start']]
                
#                 # Only group if: same emoji AND only whitespace between them
#                 if next_emoji == current_emoji and between_text.strip() == '':
#                     emoji_sequence += between_text + next_emoji
#                     end_pos = next_emoji_data['match_end']
#                     i += 1
#                 else:
#                     break
            
#             # Store the emoji sequence and add invisible marker
#             replacements.append(('emoji', emoji_sequence))
#             result.append(self.EMOJI_MARKER)
            
#             last_end = end_pos
#             i += 1
        
#         # Add remaining text
#         result.append(text[last_end:])
        
#         return ''.join(result), replacements
    
#     # 3️⃣ --- Normalization ---
#     def normalize(self, text: str) -> str:
#         """Expand contractions, run light cleanup, and leave markers untouched."""
#         # Expand contractions
#         text = contractions.fix(text)
        
#         # Basic cleanup – spacing, punctuation normalisation
#         text = re.sub(r'\s+', ' ', text).strip()
#         text = re.sub(r'([!?.,])\1+', r'\1', text)
#         return text
    
#     # 4️⃣ --- Combined Function ---
#     def clean_and_normalize(self, text: str) -> dict:
#         """Run preclean → mask_specials → normalize."""
#         precleaned = self.preclean(text)
#         masked_text, replacements = self.mask_specials(precleaned)
#         normalized = self.normalize(masked_text)
        
#         return {
#             "original_text": text,
#             "cleaned_text": normalized,
#             "replacements": replacements,  # Ordered list for restoration
#         }
    
#     # 5️⃣ --- Restoration ---
#     def restore_specials(self, text: str, replacements: list) -> str:
#         """
#         Restore URLs and emojis from their invisible markers in order.
#         Works by finding markers and replacing them sequentially.
#         """
#         # Process in order of appearance
#         for marker_type, original_content in replacements:
#             if marker_type == 'emoji':
#                 # Find and replace the FIRST occurrence of emoji marker
#                 text = text.replace(self.EMOJI_MARKER, original_content, 1)
#             elif marker_type == 'url':
#                 # Find and replace the FIRST occurrence of URL marker
#                 text = text.replace(self.URL_MARKER, original_content, 1)
        
#         return text


# if __name__ == "__main__":
#     service = NormalizeService()
    
#     sample_text = """Hey55there!! 😄🤗🤗🤗🤗🤗🤗🤗🤗🤗🤗🤗🤗🤗 I dont recently came across this super cant cool article on https://openai.com about AI writing — it's honestly mind-blowing 🤯!! The way these tools can mimic human creativity is just awesome, though sometimes the tone feels a bit robotic 😅. 
# BTW, if you wanna check some😁😁😁😁😁😁😁😂😂😂😂😂😂😂 examples, visit www.medium.com or follow my updates on Twitter @ayushi_ai 🤗🤗🤗🤗🤗🤗🤗🤗🤗🤗🤗🤗. 
# Also, I think AI shouldn't replace writers but empower them to write faster & better 💪!! What do you think??"""
    
#     result = service.clean_and_normalize(sample_text)
    
#     print("\n🔹 Original Text:")
#     print(sample_text)
    
#     print("\n🔹 After Preclean + Mask + Normalize:")
#     print(result["cleaned_text"])
#     print("\n👁️ Look carefully - the emojis and URLs are replaced with INVISIBLE markers!")
#     print("   (You can't see them, but they're there as zero-width characters)")
    
#     print("\n🔹 Replacement Order (for restoration):")
#     for i, (marker_type, original) in enumerate(result["replacements"], 1):
#         print(f"  {i}. [{marker_type.upper()}] → {repr(original)}")
    
#     print(f"\n📊 Total replacements: {len(result['replacements'])}")
    
#     # Test restoration
#     print("\n🔹 After Restoration:")
#     restored = service.restore_specials(result["cleaned_text"], result["replacements"])
#     print(restored)
    
#     # Verify restoration is perfect
#     original_no_digits = re.sub(r'\d+', '', sample_text)
#     original_normalized = re.sub(r'\s+', ' ', original_no_digits).strip()
#     restored_normalized = re.sub(r'\s+', ' ', restored).strip()
    
#     print(f"\n✅ Restoration Perfect: {original_normalized == restored_normalized}")
    
#     # Demonstrate the markers exist but are invisible
#     print("\n🔬 Technical proof that markers exist:")
#     print(f"   Cleaned text length: {len(result['cleaned_text'])} chars")
#     print(f"   Without markers: ~{len(result['cleaned_text'].replace(service.EMOJI_MARKER, '').replace(service.URL_MARKER, ''))} chars")
#     print(f"   Difference: {result['cleaned_text'].count(service.EMOJI_MARKER)} emoji markers + {result['cleaned_text'].count(service.URL_MARKER)} URL markers")


# services/normalize_service.py
import re, html, emoji, unicodedata, contractions
from textblob import TextBlob
import language_tool_python
from cleantext import clean

tool = language_tool_python.LanguageTool('en-US')


class NormalizeService:
    """Handles pre-cleaning, masking, normalization, and restoration before LLM processing."""

    # 1️⃣ --- Pre-cleaning ---
    def preclean(self, text: str) -> str:
        """Remove HTML, digits, extra spaces; keep links and emojis."""
        text = html.unescape(re.sub(r'<.*?>', '', text))
        text = unicodedata.normalize("NFKC", text)
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'([!?.,])\1+', r'\1', text)
        text = re.sub(r'[\r\n\t]+', ' ', text)
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


if __name__ == "__main__":
    service = NormalizeService()
    sample_text = """Hey there!! 😄 I dont recently came across this super cant cool article on https://openai.com about AI writing — it’s honestly mind-blowing 🤯!! The way these tools can mimic human creativity is just awesome, though sometimes the tone feels a bit robotic 😅. 
BTW, if you wanna check some examples, visit www.medium.com or follow my updates on Twitter @ayushi_ai 🤗. 
Also, I think AI shouldn’t replace writers but empower them to write faster & better 💪!! What do you think??"""

    result = service.clean_and_normalize(sample_text)

    print("\n🔹 Original Text:")
    print(sample_text)
    print("\n🔹 After Preclean + Mask + Normalize:")
    print(result["cleaned_text"])
    print("\n🔹 Restored Text:")
    print(result["restored_text"])
    print("\n🔹 Mask Mapping:")
    print(result["mask_map"])
