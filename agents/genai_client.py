import os

class _MockResponse:
    def __init__(self, text: str = ""):
        self.text = text

class _MockModel:
    def generate_content(self, model: str, contents: str) -> _MockResponse:
        # Without an API key there is nothing to verify or summarize.
        # Return "YES" so the critique stage does not incorrectly veto facts,
        # and return "" for everything else (summarizer/quiz) so they fall
        # through to their own heuristic/template fallbacks.
        if "fact-verifier" in contents or "Answer YES" in contents:
            return _MockResponse(text="YES")
        return _MockResponse(text="")

class _MockClient:
    def __init__(self):
        self.models = _MockModel()

def get_client():
    """Return a real genai.Client if GEMINI_API_KEY is set, otherwise a mock.
    The mock implements the minimal interface used by agents (models.generate_content).
    """
    if os.getenv("GEMINI_API_KEY"):
        from google import genai
        return genai.Client()
    return _MockClient()
