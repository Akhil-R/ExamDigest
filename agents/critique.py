# Copyright (c) 2026 MyCompany LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List, Dict, Any

class CritiqueAgent:
    """Mock Critique / Verifier stage.
    
    Checks generated facts for quality constraints (e.g. source URL completeness).
    """
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
