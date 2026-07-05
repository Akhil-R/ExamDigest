
from typing import List, Dict, Any, AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

class CritiqueAgent(BaseAgent):
    """Mock Critique / Verifier stage.
    
    Checks generated facts for quality constraints (e.g. source URL completeness).
    """
    name: str = "critique"

    def __init__(self, name: str = "critique", **kwargs):
        super().__init__(name=name, **kwargs)

    def verify(self, facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Verifies digest facts and filters out any items that fail quality controls."""
        print(f"[CritiqueAgent] Verifying {len(facts)} facts against quality standards.")
        verified_facts = []
        for fact in facts:
            # Let's verify that a source URL exists and looks valid (e.g. starts with http)
            url = fact.get("source_url", "")
            if not url.startswith("http://") and not url.startswith("https://"):
                print(f"[CritiqueAgent] Fact '{fact['title']}' failed verification: Invalid URL '{url}'")
                continue
            
            # Verify fact length is sufficient
            if len(fact.get("fact", "")) < 20:
                print(f"[CritiqueAgent] Fact '{fact['title']}' failed verification: Fact content too short.")
                continue
                
            verified_facts.append(fact)
            
        print(f"[CritiqueAgent] Verification complete. {len(verified_facts)}/{len(facts)} facts approved.")
        return verified_facts

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        digest_facts = ctx.session.state.get("digest_facts", [])
        verified_facts = self.verify(digest_facts)
        yield Event(
            author=self.name,
            state={"verified_facts": verified_facts}
        )
