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


class Summarizer:
    """Summarizer stage.

    Summarizes raw filtered articles into structured exam-ready facts.
    """

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
