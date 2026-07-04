import unittest

from agents.summarizer import Summarizer
from agents.quiz import QuizGenerator


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


if __name__ == "__main__":
    unittest.main()
