import language_tool_python

class GrammarService:
    """
    Provides grammar and style correction using LanguageTool.
    Independent module – can be imported or run directly.
    """

    def __init__(self, lang: str = "en-US"):
        # Initialize the grammar checker
        self.tool = language_tool_python.LanguageTool(lang)

    def correct_text(self, text: str, passes: int = 2) -> str:
        for _ in range(passes):
            matches = self.tool.check(text)
            corrected = language_tool_python.utils.correct(text, matches)
            if corrected == text:
                break
            text = corrected
        return text

    def detect_issues(self, text: str):
        """
        Returns a detailed list of detected grammar issues.
        """
        if not text or not isinstance(text, str):
            return []

        matches = self.tool.check(text)
        issues = [
            {
                "offset": m.offset,
                "error_length": m.errorLength,
                "rule_id": m.ruleId,
                "message": m.message,
                "suggestions": m.replacements,
            }
            for m in matches
        ]
        return issues


# ✅ Run standalone for testing
# if __name__ == "__main__":
#     print("\n🧩 Testing GrammarService...\n")
#     service = GrammarService()

#     sample_text = (
#         "He go to school everyday and dont like maths. "
#         "Its raining since two days, so he didnt went outside."
#     )

#     print("Original Text:\n", sample_text)
#     print("\nDetected Issues:")
#     issues = service.detect_issues(sample_text)
#     for i, issue in enumerate(issues, 1):
#         print(f"{i}. [{issue['rule_id']}] {issue['message']} → Suggestions: {issue['suggestions']}")

#     corrected = service.correct_text(sample_text)
#     print("\n✅ Corrected Text:\n", corrected)
