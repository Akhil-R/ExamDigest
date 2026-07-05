
from typing import List, Dict, Any, AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

class Summarizer(BaseAgent):
    """Summarizer stage.

    Summarizes raw filtered articles into structured exam-ready facts.
    """
    name: str = "summarizer"

    def __init__(self, name: str = "summarizer", **kwargs):
        super().__init__(name=name, **kwargs)

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

            summary = content.split(".")[0].strip()
            if len(summary) > 120:
                summary = summary[:117].rstrip() + "..."

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

