
from typing import List, Dict, Any, AsyncGenerator
import logging

from google import genai
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

logger = logging.getLogger(__name__)

_GEMINI_MODEL = "gemini-2.0-flash"


class Summarizer(BaseAgent):
    """Summarizer stage.

    Summarizes raw filtered articles into structured exam-ready facts.
    Uses Gemini to generate a crisp exam-ready sentence; falls back to
    the first-sentence heuristic if the API call fails for any reason.
    """
    name: str = "summarizer"

    def __init__(self, name: str = "summarizer", **kwargs):
        super().__init__(name=name, **kwargs)

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _summarize_with_gemini(self, content: str, tags: List[str]) -> str:
        """Return one exam-ready fact sentence via Gemini.

        Raises on any error so the caller can fall back gracefully.
        """
        topic_tags = ", ".join(tags[:3]) if tags else "general current affairs"
        prompt = (
            "You are an expert summarizer for competitive exam aspirants in India "
            f"(topics: {topic_tags}).\n\n"
            "Write exactly ONE concise sentence (max 120 characters) that captures "
            "the most exam-relevant fact from the passage below. "
            "Do NOT add bullet points, headings, or markdown — plain text only.\n\n"
            f"Passage:\n{content[:1500]}"
        )
        if not hasattr(self, "_client") or self._client is None:
            self._client = genai.Client()
        response = self._client.models.generate_content(model=_GEMINI_MODEL, contents=prompt)
        text = (response.text or "").strip()
        if len(text) > 120:
            text = text[:117].rstrip() + "..."
        return text

    def _heuristic_summary(self, content: str) -> str:
        """Original first-sentence heuristic — used as fallback."""
        summary = content.split(".")[0].strip()
        if len(summary) > 120:
            summary = summary[:117].rstrip() + "..."
        return summary

    # ------------------------------------------------------------------ #
    # Public interface                                                     #
    # ------------------------------------------------------------------ #

    def summarize(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rewrites news items into concise exam-style facts with a clear takeaway."""
        print(f"[Summarizer] Summarizing {len(articles)} articles into exam-ready facts.")
        facts = []
        for index, article in enumerate(articles, 1):
            content = article.get("content", "").strip()
            tags = article.get("tags", []) or []
            topic_tags = ", ".join(tags[:3]) if tags else "general current affairs"

            if not content:
                content = "The development is relevant for exam preparation and should be reviewed in detail."

            # Try Gemini; fall back to heuristic on any error
            try:
                summary = self._summarize_with_gemini(content, tags)
                logger.debug("[Summarizer] Gemini summary for '%s'", article.get("title", ""))
            except Exception as exc:
                logger.warning("[Summarizer] Gemini call failed (%s); using heuristic.", exc)
                summary = self._heuristic_summary(content)

            fact_text = f"{summary} Why it matters: relevant to {topic_tags}."
            fact_text = " ".join(fact_text.split())
            facts.append(
                {
                    "id": index,
                    "title": article["title"],
                    "fact": fact_text,
                    "source_url": article["url"],
                    "tags": tags,
                }
            )
        return facts

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        filtered_articles = ctx.session.state.get("filtered_articles", [])
        digest_facts = self.summarize(filtered_articles)
        yield Event(
            author=self.name,
            state={"digest_facts": digest_facts}
        )
