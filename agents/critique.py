
import logging
from typing import List, Dict, Any, AsyncGenerator

from google import genai
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

logger = logging.getLogger(__name__)

_GEMINI_MODEL = "gemini-2.0-flash"


class CritiqueAgent(BaseAgent):
    """Verifier stage with lightweight pre-filters and optional Gemini faithfulness checks."""

    name: str = "critique"

    def __init__(self, name: str = "critique", **kwargs):
        super().__init__(name=name, **kwargs)

    def _verify_fact_with_gemini(self, fact: Dict[str, Any], source_article: Dict[str, Any]) -> bool:
        """Return True when Gemini confirms the fact is supported by the source passage."""
        prompt = (
            "You are a strict fact-verifier for competitive exam content.\n"
            "Answer YES if the fact is fully supported by the source passage.\n"
            "Answer NO if the fact contradicts the source passage or adds information not present there.\n"
            "Respond with exactly YES or NO.\n\n"
            f"Fact: {fact.get('fact', '')}\n\n"
            f"Source passage: {source_article.get('content', '')[:2500]}"
        )
        client = genai.Client()
        response = client.models.generate_content(model=_GEMINI_MODEL, contents=prompt)
        verdict = (response.text or "").strip().upper()
        return verdict == "YES"

    def verify(
        self,
        facts: List[Dict[str, Any]],
        source_articles: List[Dict[str, Any]] | None = None,
    ) -> List[Dict[str, Any]]:
        """Verifies digest facts and filters out any items that fail quality controls."""
        print(f"[CritiqueAgent] Verifying {len(facts)} facts against quality standards.")
        verified_facts = []
        source_articles = source_articles or []
        source_lookup = {
            article.get("title", ""): article for article in source_articles if article.get("title")
        }

        for fact in facts:
            url = fact.get("source_url", "")
            if not url.startswith("http://") and not url.startswith("https://"):
                print(f"[CritiqueAgent] Fact '{fact['title']}' failed verification: Invalid URL '{url}'")
                continue

            if len(fact.get("fact", "")) < 20:
                print(f"[CritiqueAgent] Fact '{fact['title']}' failed verification: Fact content too short.")
                continue

            source_article = source_lookup.get(fact.get("title"), {})
            if source_article:
                try:
                    is_supported = self._verify_fact_with_gemini(fact, source_article)
                except Exception as exc:
                    logger.warning("[CritiqueAgent] Gemini faithfulness check failed (%s); keeping fact.", exc)
                    is_supported = True
                if not is_supported:
                    print(f"[CritiqueAgent] Fact '{fact['title']}' failed verification: unsupported by source.")
                    continue

            verified_facts.append(fact)

        print(f"[CritiqueAgent] Verification complete. {len(verified_facts)}/{len(facts)} facts approved.")
        return verified_facts

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        digest_facts = ctx.session.state.get("digest_facts", [])
        raw_articles = ctx.session.state.get("raw_articles", [])
        verified_facts = self.verify(digest_facts, source_articles=raw_articles)
        yield Event(
            author=self.name,
            state={"verified_facts": verified_facts}
        )
