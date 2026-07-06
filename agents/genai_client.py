import os

class _MockResponse:
    def __init__(self, text: str = ""):
        self.text = text

class _MockModel:
    def generate_content(self, model: str, contents: str) -> _MockResponse:
        # Return empty text to trigger heuristic fallback.
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
