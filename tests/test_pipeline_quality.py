import unittest
from unittest.mock import patch

from agents.live_collector import LiveNewsCollector
from agents.summarizer import Summarizer
from agents.quiz import QuizGenerator

try:
    from server.app import _validate_data_mode
except ModuleNotFoundError:
    _validate_data_mode = None


class SummarizerQualityTests(unittest.TestCase):
    def test_summarize_creates_concise_exam_ready_facts(self):
        summarizer = Summarizer()
        article = {
            "title": "Kerala Launches Digital Access Scheme",
            "content": "The government has introduced a new digital access scheme aimed at expanding public services to rural households.",
            "url": "https://example.com/news",
            "tags": ["Kerala Governance", "State Schemes"],
        }

        facts = summarizer.summarize([article])

        self.assertEqual(len(facts), 1)
        fact_text = facts[0]["fact"]
        self.assertIn("Why it matters", fact_text)
        self.assertIn("Kerala Governance", fact_text)
        self.assertLessEqual(len(fact_text), 220)


class QuizGeneratorTests(unittest.TestCase):
    def test_generate_quiz_returns_five_structured_questions(self):
        generator = QuizGenerator()
        facts = [
            {
                "title": "Kerala Launches Digital Access Scheme",
                "fact": "Kerala launched a new scheme to improve digital access in rural areas.",
                "source_url": "https://example.com/news",
                "tags": ["Kerala Governance", "State Schemes"],
            }
        ]

        quiz = generator.generate_quiz(facts)

        self.assertEqual(len(quiz), 5)
        self.assertTrue(all("question" in question for question in quiz))
        self.assertTrue(all(len(question["options"]) == 4 for question in quiz))

    def test_generate_quiz_returns_empty_list_for_empty_facts(self):
        generator = QuizGenerator()

        quiz = generator.generate_quiz([])

        self.assertEqual(quiz, [])


class LiveNewsCollectorTests(unittest.TestCase):
    def test_gdelt_articles_are_normalized_and_deduplicated(self):
        collector = LiveNewsCollector(
            source_config_path="data/source_config.json",
            cache_dir="data/cache",
        )
        payload = """
        {
          "articles": [
            {"title": "Kerala launches public service reform", "url": "https://example.com/a", "domain": "example.com"},
            {"title": "Kerala launches public service reform", "url": "https://example.com/a", "domain": "example.com"},
            {"title": "", "url": "https://example.com/empty", "domain": "example.com"},
            {"title": "Bad URL", "url": "not-a-url", "domain": "example.com"}
          ]
        }
        """

        with patch.object(collector, "_fetch_text", return_value=payload):
            articles = collector._collect_gdelt(
                "Kerala public service",
                ["Kerala Governance", "State Schemes"],
            )

        deduped = collector._dedupe_articles(articles)
        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0]["title"], "Kerala launches public service reform")
        self.assertEqual(deduped[0]["url"], "https://example.com/a")
        self.assertIn("Kerala Governance", deduped[0]["tags"])

    def test_collect_stops_after_first_successful_gdelt_query(self):
        collector = LiveNewsCollector(
            source_config_path="data/source_config.json",
            cache_dir="data/cache",
        )
        config = {
            "rss_feeds": [],
            "gdelt_queries": ["first query", "second query"],
            "default_tags": ["State Schemes"],
        }
        first_result = [
            {
                "title": "Kerala launches a public service scheme",
                "content": "The state government launched a new scheme.",
                "url": "https://example.com/kerala-scheme",
                "tags": ["State Schemes"],
            }
        ]

        with patch.object(collector, "_load_exam_config", return_value=config), patch.object(
            collector, "_collect_gdelt", side_effect=[first_result, []]
        ) as mock_collect_gdelt:
            articles = collector.collect("psc")

        self.assertEqual(len(articles), 1)
        self.assertEqual(mock_collect_gdelt.call_count, 1)
        self.assertEqual(mock_collect_gdelt.call_args_list[0].args[0], "first query")


class ApiValidationTests(unittest.TestCase):
    @unittest.skipIf(_validate_data_mode is None, "FastAPI is not installed")
    def test_validate_data_mode_accepts_supported_modes(self):
        self.assertEqual(_validate_data_mode("mock"), "mock")
        self.assertEqual(_validate_data_mode("LIVE"), "live")

    @unittest.skipIf(_validate_data_mode is None, "FastAPI is not installed")
    def test_validate_data_mode_rejects_unknown_mode(self):
        with self.assertRaises(Exception):
            _validate_data_mode("paid")


if __name__ == "__main__":
    unittest.main()
