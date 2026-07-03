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

from typing import List, Dict, Any, Set

class RelevanceFilter:
    """Mock Relevance Filter stage.
    
    Scores and filters collected articles based on syllabus tags and checks them
    against the seen topics history (memory) to avoid duplicates.
    """
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
        print(f"[RelevanceFilter] Filter complete. Returning {len(result)} articles (min={min_items}, max={max_items}).")
        return result
