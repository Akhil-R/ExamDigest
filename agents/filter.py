
from typing import List, Dict, Any, Set, AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

class RelevanceFilter(BaseAgent):
    """Mock Relevance Filter stage.
    
    Scores and filters collected articles based on syllabus tags and checks them
    against the seen topics history (memory) to avoid duplicates.
    """
    name: str = "filter"

    def __init__(self, name: str = "filter", **kwargs):
        super().__init__(name=name, **kwargs)

    def filter(
        self, 
        articles: List[Dict[str, Any]], 
        syllabus_tags: List[str], 
        seen_topics: List[str],
        min_items: int = 8,
        max_items: int = 12
    ) -> List[Dict[str, Any]]:
        """Filters articles to match syllabus tags and deduplicate against seen topics."""
        print(f"[RelevanceFilter] Filtering articles using syllabus tags: {syllabus_tags}")
        print(f"[RelevanceFilter] Excluding already seen topics: {seen_topics}")
        
        seen_set = set(seen_topics)
        filtered_articles = []
        
        for article in articles:
            # Check for memory overlap (deduplication)
            # If the article title or URL was already seen, skip it
            if article["title"] in seen_set or article["url"] in seen_set:
                print(f"[RelevanceFilter] Skipping seen article: {article['title']}")
                continue
            
            # Check relevance to syllabus tags
            # The article must have at least one overlapping tag with the exam's syllabus tags
            overlap = set(article["tags"]).intersection(set(syllabus_tags))
            if overlap:
                filtered_articles.append(article)
                print(f"[RelevanceFilter] Keep relevant article: {article['title']} (matched tags: {list(overlap)})")
        
        # Limit to the max constraint (8-12 items)
        result = filtered_articles[:max_items]
        if len(result) < min_items:
            print(
                f"[RelevanceFilter] Only {len(result)} articles remain after filtering; using the available items."
            )
        print(f"[RelevanceFilter] Filter complete. Returning {len(result)} articles (min={min_items}, max={max_items}).")
        return result

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        raw_articles = ctx.session.state.get("raw_articles", [])
        syllabus_tags = ctx.session.state.get("syllabus_tags", [])
        seen_topics = ctx.session.state.get("seen_topics", [])
        filtered_articles = self.filter(raw_articles, syllabus_tags, seen_topics)
        yield Event(
            author=self.name,
            state={"filtered_articles": filtered_articles}
        )
