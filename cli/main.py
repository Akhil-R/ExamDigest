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

# Adjust path to import from workspace root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.collector import NewsCollector
from agents.filter import RelevanceFilter
from agents.summarizer import Summarizer
from agents.critique import CritiqueAgent
from agents.quiz import QuizGenerator


def _get_paths() -> dict:
    """Return base directory paths for data and outputs."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return {
        "base": base_dir,
        "data": os.path.join(base_dir, "data"),
        "outputs": os.path.join(base_dir, "outputs"),
        "syllabus": os.path.join(base_dir, "data", "syllabus_tags.json"),
        "seen_topics": os.path.join(base_dir, "data", "seen_topics.json"),
    }


def reset_memory() -> str:
    """Clears the seen_topics.json memory store."""
    paths = _get_paths()
    os.makedirs(paths["data"], exist_ok=True)
    with open(paths["seen_topics"], "w") as f:
        json.dump([], f, indent=2)
    return paths["seen_topics"]


def run_pipeline(exam_type: str) -> tuple:
    """Executes the staged agent workflow for the specified exam type.
    
    Workflow: News Collector → Relevance Filter → Summarizer → Critique → Quiz → Memory
    
    Returns:
        Tuple of (verified_facts, quiz_questions)
    """
    paths = _get_paths()

    # Create directories if they don't exist
    os.makedirs(paths["data"], exist_ok=True)
    os.makedirs(paths["outputs"], exist_ok=True)

    # Load syllabus tags
    if not os.path.exists(paths["syllabus"]):
        raise FileNotFoundError(
            f"Syllabus tags not found at {paths['syllabus']}. Please create data/syllabus_tags.json."
        )
    with open(paths["syllabus"], "r") as f:
        syllabus_data = json.load(f)

    exam_tags = syllabus_data.get(exam_type.lower(), [])
    if not exam_tags:
        print(f"⚠  Warning: No syllabus tags defined for exam type: {exam_type}")

    # Load seen topics (deduplication memory)
    seen_topics: list = []
    if os.path.exists(paths["seen_topics"]):
        try:
            with open(paths["seen_topics"], "r") as f:
                seen_topics = json.load(f)
        except json.JSONDecodeError:
            print("⚠  seen_topics.json is corrupt — resetting to empty list.")
            seen_topics = []

    print(f"\n{'='*55}")
    print(f"  📋  ExamDigest Pipeline  |  Exam: {exam_type.upper()}")
    print(f"{'='*55}")

    # ── Stage 1: News Collector ──────────────────────────────
    print("\n  🔍  Stage 1/5 — News Collection")
    collector = NewsCollector()
    raw_articles = collector.collect(exam_type)
    print(f"     Collected {len(raw_articles)} raw articles.")

    # ── Stage 2: Relevance Filter ────────────────────────────
    print("\n  🏷   Stage 2/5 — Relevance Filtering & Deduplication")
    r_filter = RelevanceFilter()
    filtered_articles = r_filter.filter(raw_articles, exam_tags, seen_topics)
    print(f"     {len(filtered_articles)} articles passed filter.")

    # ── Stage 3: Summarizer ──────────────────────────────────
    print("\n  ✍   Stage 3/5 — Fact Summarization")
    summarizer = Summarizer()
    digest_facts = summarizer.summarize(filtered_articles)
    if not digest_facts and filtered_articles:
        print("     No facts were produced after filtering; using the available items as a fallback.")
    print(f"     Generated {len(digest_facts)} exam-ready facts.")

    # ── Stage 4: Critique / Verifier ─────────────────────────
    print("\n  🔎  Stage 4/5 — Quality Verification")
    critique = CritiqueAgent()
    verified_facts = critique.verify(digest_facts)
    print(f"     {len(verified_facts)}/{len(digest_facts)} facts approved.")

    # ── Stage 5: Quiz Generator ──────────────────────────────
    print("\n  ❓  Stage 5/5 — Quiz Generation")
    quiz_generator = QuizGenerator()
    quiz = quiz_generator.generate_quiz(verified_facts)
    print(f"     Generated {len(quiz)} MCQ questions.")

    # ── Memory Update ────────────────────────────────────────
    new_seen = (
        [fact["title"] for fact in verified_facts]
        + [fact["source_url"] for fact in verified_facts]
    )
    updated_seen = list(set(seen_topics + new_seen))
    with open(paths["seen_topics"], "w") as f:
        json.dump(updated_seen, f, indent=2)
    print(f"\n  💾  Memory updated ({len(updated_seen)} entries stored).")

    # ── Write Output Files ───────────────────────────────────
    today_str = datetime.now().strftime("%Y-%m-%d")

    # digest.md
    digest_path = os.path.join(paths["outputs"], "digest.md")
    digest_lines = [
        f"# Current Affairs Digest ({exam_type.upper()}) — {today_str}",
        "",
        "> ⚠  **SIMULATION DEMO**: This digest is generated from mock data for",
        "> educational and demonstration purposes. It does not represent official",
        "> exam notifications or real-time news.",
        "",
    ]
    if not verified_facts:
        digest_lines.append(
            "No new current affairs relevant to this exam type were found. "
            "Try resetting the memory with `python cli/main.py --reset-memory` to revisit the full dataset."
        )
    else:
        for i, fact in enumerate(verified_facts, 1):
            digest_lines += [
                f"## Fact {i}: {fact['title']}",
                f"- **Summary:** {fact['fact']}",
                f"- **Source:** <{fact['source_url']}>",
                f"- **Tags:** {', '.join(fact['tags'])}",
                "",
            ]

    with open(digest_path, "w") as f:
        f.write("\n".join(digest_lines))
    print(f"  📄  Digest saved → {digest_path}")

    # quiz.json
    quiz_path = os.path.join(paths["outputs"], "quiz.json")
    with open(quiz_path, "w") as f:
        json.dump(quiz, f, indent=2)
    print(f"  📝  Quiz saved   → {quiz_path}")

    print(f"\n{'='*55}\n")
    return verified_facts, quiz


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ExamDigest — Current Affairs Digest Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli/main.py --exam psc
  python cli/main.py --exam ssc
  python cli/main.py --exam railway
  python cli/main.py --reset-memory
  python cli/main.py --exam psc --reset-memory
        """,
    )
    parser.add_argument(
        "--exam",
        choices=["psc", "ssc", "railway"],
        help="Target exam type (psc, ssc, railway)",
    )
    parser.add_argument(
        "--reset-memory",
        action="store_true",
        help="Clear the seen_topics.json deduplication memory and exit",
    )
    args = parser.parse_args()

    if args.reset_memory:
        path = reset_memory()
        print(f"✅  Memory cleared: {path}")

    if args.exam:
        run_pipeline(args.exam)
        print("✅  Workflow completed successfully!")
    elif not args.reset_memory:
        parser.print_help()
