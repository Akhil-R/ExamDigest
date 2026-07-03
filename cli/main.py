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

import argparse
import json
import os
import sys
from datetime import datetime

# Adjust path to import from agents directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.collector import NewsCollector
from agents.filter import RelevanceFilter
from agents.summarizer import Summarizer
from agents.critique import CritiqueAgent
from agents.quiz import QuizGenerator

def run_pipeline(exam_type: str) -> tuple:
    """Executes the staged agent workflow for the specified exam type.
    
    Workflow: News Collector -> Relevance Filter -> Summarizer -> Quiz -> Critique -> Memory
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    outputs_dir = os.path.join(base_dir, "outputs")
    
    # Create directories if they don't exist
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)
    
    syllabus_path = os.path.join(data_dir, "syllabus_tags.json")
    seen_topics_path = os.path.join(data_dir, "seen_topics.json")
    
    # Load syllabus tags
    if not os.path.exists(syllabus_path):
        raise FileNotFoundError(f"Syllabus tags not found at {syllabus_path}. Please create it first.")
    with open(syllabus_path, "r") as f:
        syllabus_data = json.load(f)
    
    exam_tags = syllabus_data.get(exam_type.lower(), [])
    if not exam_tags:
        print(f"Warning: No tags defined for exam type: {exam_type}")
    
    # Load seen topics
    seen_topics = []
    if os.path.exists(seen_topics_path):
        try:
            with open(seen_topics_path, "r") as f:
                seen_topics = json.load(f)
        except json.JSONDecodeError:
            print("Warning: seen_topics.json is empty or corrupt. Initializing as empty list.")
            seen_topics = []

    print(f"\n--- Starting Workflow for {exam_type.upper()} Exam ---")
    
    # 1. News Collector
    collector = NewsCollector()
    raw_articles = collector.collect(exam_type)
    
    # 2. Relevance Filter
    r_filter = RelevanceFilter()
    filtered_articles = r_filter.filter(raw_articles, exam_tags, seen_topics)
    
    # 3. Summarizer
    summarizer = Summarizer()
    digest_facts = summarizer.summarize(filtered_articles)
    
    # 4. Critique / Verifier
    critique = CritiqueAgent()
    verified_facts = critique.verify(digest_facts)
    
    # 5. Quiz Generator
    quiz_generator = QuizGenerator()
    quiz = quiz_generator.generate_quiz(verified_facts)
    
    # 6. Memory Update
    # Update seen topics list with the titles/URLs of processed facts
    new_seen = [fact["title"] for fact in verified_facts] + [fact["source_url"] for fact in verified_facts]
    updated_seen_topics = list(set(seen_topics + new_seen))
    with open(seen_topics_path, "w") as f:
        json.dump(updated_seen_topics, f, indent=2)
    print(f"[Memory] Updated seen topics database at {seen_topics_path}")
    
    # Write output files
    digest_path = os.path.join(outputs_dir, "digest.md")
    quiz_path = os.path.join(outputs_dir, "quiz.json")
    
    # Format and save digest.md
    today_str = datetime.now().strftime("%Y-%m-%d")
    digest_md_content = f"# Current Affairs Digest ({exam_type.upper()}) - {today_str}\n\n"
    if not verified_facts:
        digest_md_content += "No new current affairs relevant to this exam type were found today.\n"
    else:
        for i, fact in enumerate(verified_facts, 1):
            digest_md_content += f"## Fact {i}: {fact['title']}\n"
            digest_md_content += f"- **Fact:** {fact['fact']}\n"
            digest_md_content += f"- **Source URL:** {fact['source_url']}\n"
            digest_md_content += f"- **Tags:** {', '.join(fact['tags'])}\n\n"
            
    with open(digest_path, "w") as f:
        f.write(digest_md_content)
    print(f"[Output] Digest written to {digest_path}")
    
    # Format and save quiz.json
    with open(quiz_path, "w") as f:
        json.dump(quiz, f, indent=2)
    print(f"[Output] Quiz written to {quiz_path}")
    
    return verified_facts, quiz

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Current Affairs Digest Agent CLI")
    parser.add_argument(
        "--exam",
        choices=["psc", "ssc", "railway"],
        required=True,
        help="Target exam type (psc, ssc, railway)"
    )
    args = parser.parse_args()
    
    run_pipeline(args.exam)
    print("\nWorkflow completed successfully!")
