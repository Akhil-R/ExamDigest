import json
import logging
from typing import List, Dict, Any, AsyncGenerator

from google import genai
from pydantic import PrivateAttr
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

logger = logging.getLogger(__name__)

_GEMINI_MODEL = "gemini-2.0-flash"

class QuizGenerator(BaseAgent):
    """Quiz Generator stage.

    Generates 5 multiple-choice questions based on final verified digest facts.
    """
    name: str = "quiz"

    _question_db: Dict[str, Any] = PrivateAttr()

    def __init__(self, name: str = "quiz", **kwargs):
        super().__init__(name=name, **kwargs)
        self._question_db = {
            "Vizhinjam International Seaport Commissions Phase-1 Operations": {
                "question": "Which state in India is home to the Vizhinjam International Seaport, which recently commissioned its Phase-1 operations?",
                "options": ["Kerala", "Tamil Nadu", "Karnataka", "Andhra Pradesh"],
                "correct_answer": "Kerala",
                "explanation": "Vizhinjam International Seaport is India's first deepwater transshipment port, located in Thiruvananthapuram, Kerala, and managed in partnership with the Government of Kerala."
            },
            "Kerala Fiber Optic Network (KFON) Launches Phase-2 Expansion": {
                "question": "What is the primary objective of the Kerala Fiber Optic Network (KFON) project?",
                "options": [
                    "To provide free high-speed internet to BPL families and government offices",
                    "To establish a statewide satellite communication system",
                    "To build new roads and highway infrastructure",
                    "To digitize local agriculture credit societies"
                ],
                "correct_answer": "To provide free high-speed internet to BPL families and government offices",
                "explanation": "KFON aims to bridge the digital divide by providing high-speed internet connectivity to below-poverty-line (BPL) families and government offices in Kerala."
            },
            "Kerala's K-Smart Application Launched for Unified Local Body Services": {
                "question": "What does the 'K-Smart' application launched by the Kerala government stand for?",
                "options": [
                    "Kerala Solution for Managing Administrative Reformation and Transformation",
                    "Kerala System for Municipal and Rural Transport",
                    "Kerala Science and Technology Management Portal",
                    "Kerala State Market and Agricultural Resource Tracker"
                ],
                "correct_answer": "Kerala Solution for Managing Administrative Reformation and Transformation",
                "explanation": "K-Smart stands for Kerala Solution for Managing Administrative Reformation and Transformation. It digitizes administrative services across all local bodies."
            },
            "India's First Digital Science Park Commences in Trivandrum": {
                "question": "Where is India's first Digital Science Park being established?",
                "options": ["Thiruvananthapuram, Kerala", "Bengaluru, Karnataka", "Hyderabad, Telangana", "Pune, Maharashtra"],
                "correct_answer": "Thiruvananthapuram, Kerala",
                "explanation": "The foundation stone for India's first Digital Science Park was laid in Thiruvananthapuram (Trivandrum), Kerala, focusing on AI, robotics, and smart hardware."
            },
            "Kerala Literacy Mission Announces 'Aksharasree' Program Expansion": {
                "question": "The 'Aksharasree' continuing education project launched by the State Literacy Mission of Kerala focuses on which areas?",
                "options": [
                    "Tribal colonies and remote coastal areas",
                    "Urban IT hubs and science parks",
                    "Preschool childcare centers",
                    "Overseas employment training"
                ],
                "correct_answer": "Tribal colonies and remote coastal areas",
                "explanation": "The 'Aksharasree' program is being expanded to provide equivalency education to adults in tribal colonies and remote coastal areas."
            },
            "Kudumbashree Enterprise Launches Haritha Karma Sena Waste Units": {
                "question": "The Kudumbashree network in Kerala has scaled up which service group for solid-waste management?",
                "options": ["Haritha Karma Sena", "Suchitwa Mission Volunteers", "Kudumbashree Clean Force", "Green Volunteers Club"],
                "correct_answer": "Haritha Karma Sena",
                "explanation": "Haritha Karma Sena units are scaled up by Kudumbashree in partnership with local bodies to implement scientific waste segregation and recycling."
            },
            "Supreme Court Rules on Center-State Financial Devolution": {
                "question": "Which Article of the Indian Constitution governs the establishment of the Finance Commission for Center-State devolution?",
                "options": ["Article 280", "Article 360", "Article 263", "Article 312"],
                "correct_answer": "Article 280",
                "explanation": "Article 280 of the Constitution provides for the Finance Commission, which recommends the devolution of financial resources between the Union and States."
            },
            "State Government Announces Administrative Reforms Commission": {
                "question": "What is the primary focus of an Administrative Reforms Commission (ARC)?",
                "options": [
                    "Governance restructuring and streamlining public service delivery",
                    "Amending defense and military rules",
                    "Allocating space exploration budgets",
                    "Overseeing state highway construction projects"
                ],
                "correct_answer": "Governance restructuring and streamlining public service delivery",
                "explanation": "ARCs are appointed to recommend administrative restructuring, improve governance, and optimize public service delivery mechanisms."
            },
            "ISRO Gaganyaan Crew Module Escape System Test Successful": {
                "question": "What was the name of the first Test Vehicle flight conducted by ISRO for the Gaganyaan mission?",
                "options": ["TV-D1", "G1-Mission", "LVM3-M4", "Aditya-L1"],
                "correct_answer": "TV-D1",
                "explanation": "ISRO successfully conducted the Test Vehicle Abort Mission (TV-D1) to validate the crew escape system under abort conditions."
            },
            "India Semiconductor Mission: Micron's First Fab Plant Tabled in Gujarat": {
                "question": "Under the India Semiconductor Mission (ISM), where is the first commercial semiconductor assembly facility being constructed?",
                "options": ["Sanand, Gujarat", "Bengaluru, Karnataka", "Noida, Uttar Pradesh", "Chennai, Tamil Nadu"],
                "correct_answer": "Sanand, Gujarat",
                "explanation": "Construction of India's first commercial semiconductor assembly and test facility has commenced in Sanand, Gujarat."
            },
            "Union Cabinet Approves Unified Pension Scheme (UPS)": {
                "question": "The newly approved Unified Pension Scheme (UPS) guarantees what percentage of basic salary as pension?",
                "options": [
                    "50% of the average basic pay of the last 12 months",
                    "40% of the average basic pay of the last 10 months",
                    "60% of the last drawn pay",
                    "30% of the career-average basic pay"
                ],
                "correct_answer": "50% of the average basic pay of the last 12 months",
                "explanation": "The UPS guarantees central government employees a pension equal to 50% of the average basic pay drawn in the last 12 months before retirement."
            },
            "Electoral Integrity Reform Bill Tabled in Lok Sabha": {
                "question": "Which of the following is a proposal in the Electoral Integrity Reform Bill?",
                "options": [
                    "Linking voter IDs with Aadhaar on a voluntary basis",
                    "Implementing mandatory voting for all citizens",
                    "Abolishing proxy voting entirely",
                    "Eliminating voter lists for municipal elections"
                ],
                "correct_answer": "Linking voter IDs with Aadhaar on a voluntary basis",
                "explanation": "The Bill proposes voluntary linking of voter IDs with Aadhaar and working toward a unified voter list."
            },
            "Archaeologists Discover Harappan-Era Water Systems in Rakhigarhi": {
                "question": "At which Harappan site were sophisticated burnt-brick drainage channels recently excavated?",
                "options": ["Rakhigarhi", "Lothal", "Kalibangan", "Dholavira"],
                "correct_answer": "Rakhigarhi",
                "explanation": "Recent excavations at Rakhigarhi in Haryana uncovered elaborate drainage systems of the Indus Valley Civilization."
            },
            "IMD Releases Report on Monsoon Patterns Over Western Ghats": {
                "question": "According to the IMD report on Western Ghats, what change has been observed in monsoon patterns?",
                "options": [
                    "Shifting precipitation zones and localized extreme rainfall",
                    "A uniform reduction in rain across all states",
                    "Complete absence of monsoonal wind patterns",
                    "A significant increase in snowfall along high peaks"
                ],
                "correct_answer": "Shifting precipitation zones and localized extreme rainfall",
                "explanation": "The IMD report shows shifts in precipitation patterns and increases in micro-regional extreme rainfall events over the Western Ghats."
            },
            "Indian Railways Achieves 100% Electrification of Golden Quadrilateral": {
                "question": "Which four major metro cities are connected by the Golden Quadrilateral route of Indian Railways?",
                "options": ["Delhi, Mumbai, Chennai, and Kolkata", "Delhi, Mumbai, Bengaluru, and Hyderabad", "Mumbai, Pune, Bengaluru, and Chennai", "Delhi, Jaipur, Ahmedabad, and Mumbai"],
                "correct_answer": "Delhi, Mumbai, Chennai, and Kolkata",
                "explanation": "The Golden Quadrilateral rail routes connect the four major metro cities: Delhi, Mumbai, Chennai, and Kolkata."
            },
            "Vande Bharat Sleeper Coach Prototype Unveiled by BEML": {
                "question": "Which PSU manufactured and unveiled the first prototype of the Vande Bharat Sleeper train?",
                "options": ["BEML Limited", "Integral Coach Factory (ICF)", "Rail Coach Factory (RCF)", "Bharat Heavy Electricals Limited (BHEL)"],
                "correct_answer": "BEML Limited",
                "explanation": "The first prototype of the Vande Bharat Sleeper coach was manufactured and unveiled by BEML in Bengaluru."
            },
            "Kavach 4.0 Automatic Train Protection Deployed on High-Density Routes": {
                "question": "What is the primary function of the indigenous 'Kavach' system in Indian Railways?",
                "options": [
                    "Automatic Train Protection to prevent collisions",
                    "Wi-Fi connectivity inside passenger coaches",
                    "Real-time ticket booking and allocation",
                    "Automated platform cleaning and maintenance"
                ],
                "correct_answer": "Automatic Train Protection to prevent collisions",
                "explanation": "Kavach is an Automatic Train Protection (ATP) system that prevents train collisions by automatically applying brakes if the driver overshoots signals."
            },
            "India's First Hydrogen-Powered Train Trial Scheduled on Jind-Sonipat Route": {
                "question": "On which route will Indian Railways test its first hydrogen fuel cell-powered passenger train?",
                "options": ["Jind-Sonipat", "Pathankot-Jogindernagar", "Kalka-Shimla", "Nilgiri Mountain Railway"],
                "correct_answer": "Jind-Sonipat",
                "explanation": "The first hydrogen fuel cell train trials in India are scheduled to run on the Jind-Sonipat route in Haryana."
            },
            "Historic Nilgiri Mountain Railway Inducts Custom Steam Locomotive": {
                "question": "The Nilgiri Mountain Railway, which recently inducted a new steam locomotive, is located in which state?",
                "options": ["Tamil Nadu", "Kerala", "Karnataka", "Himachal Pradesh"],
                "correct_answer": "Tamil Nadu",
                "explanation": "The Nilgiri Mountain Railway is a UNESCO World Heritage site located in the state of Tamil Nadu."
            },
            "ISRO and Indian Railways Partner for Real-Time Satellite Tracking": {
                "question": "Which satellite network system does the Real-Time Train Information System (RTIS) utilize?",
                "options": [
                    "ISRO GSAT satellites",
                    "IRNSS (NavIC) satellites",
                    "INSAT weather satellites",
                    "EOS earth observation satellites"
                ],
                "correct_answer": "ISRO GSAT satellites",
                "explanation": "The RTIS utilizes telemetry devices powered by ISRO's GSAT communications satellites to track train movements automatically."
            }
        }

    # ------------------------------------------------------------------ #
    # Gemini helper                                                        #
    # ------------------------------------------------------------------ #

    def _generate_question_with_gemini(self, fact: Dict[str, Any]) -> Dict[str, Any]:
        """Generate one MCQ for *fact* via Gemini.

        Returns a dict with keys: question, options (list[str]), correct_answer,
        explanation.  Raises on any error so the caller can fall back.
        """
        prompt = (
            "You are a quiz-setter for Indian competitive exams (PSC, SSC, Railway).\n"
            "Given the fact below, create exactly ONE multiple-choice question with:\n"
            "  - A clear question sentence\n"
            "  - Exactly 4 distinct answer options (labelled A, B, C, D internally)\n"
            "  - The correct answer text (must match one option exactly)\n"
            "  - A one-sentence explanation\n\n"
            "Return ONLY valid JSON in this exact structure, no markdown:\n"
            '{"question": "...", "options": ["...", "...", "...", "..."], '
            '"correct_answer": "...", "explanation": "..."}\n\n'
            f"Fact title: {fact['title']}\n"
            f"Fact: {fact['fact']}"
        )
        client = genai.Client()
        response = client.models.generate_content(model=_GEMINI_MODEL, contents=prompt)
        raw = (response.text or "").strip()
        # Strip accidental markdown fences if the model adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        # Basic validation
        assert isinstance(data["options"], list) and len(data["options"]) == 4
        assert data["correct_answer"] in data["options"]
        return data

    # ------------------------------------------------------------------ #
    # Public interface                                                     #
    # ------------------------------------------------------------------ #

    def generate_quiz(self, facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generates a list of 5 multiple choice questions from digest facts.

        Questions are sampled evenly across all available facts so that a large
        digest doesn't mean only the first 5 articles get covered.
        """
        print(f"[QuizGenerator] Generating 5 MCQs based on {len(facts)} digest facts.")

        if not facts:
            return []

        # Evenly sample 5 indices spread across the full facts list
        n = len(facts)
        num_q = 5
        if n <= num_q:
            selected_facts = (facts * ((num_q // n) + 1))[:num_q]
        else:
            step = n / num_q
            selected_facts = [facts[int(i * step)] for i in range(num_q)]

        questions = []
        for i, fact in enumerate(selected_facts):
            title = fact["title"]

            if title in self.question_db:
                # Use hand-crafted question from the static database
                item = self.question_db[title]
                question_text = item["question"]
                options = item["options"]
                correct_answer = item["correct_answer"]
                explanation = item["explanation"]
            else:
                # Try Gemini; fall back to template on any error
                try:
                    gemini_q = self._generate_question_with_gemini(fact)
                    question_text = gemini_q["question"]
                    options = gemini_q["options"]
                    correct_answer = gemini_q["correct_answer"]
                    explanation = gemini_q["explanation"]
                    logger.debug("[QuizGenerator] Gemini question for '%s'", title)
                except Exception as exc:
                    logger.warning("[QuizGenerator] Gemini call failed (%s); using template.", exc)
                    question_text = f"Which of the following is correct regarding '{fact['title']}'?"
                    options = [
                        f"It relates to: {fact['fact'][:60]}...",
                        "It has no relevance to competitive exams.",
                        "It was declared unconstitutional by all global courts.",
                        "It only affects private enterprise and has no government scope.",
                    ]
                    correct_answer = options[0]
                    explanation = f"Based on the digest, the correct answer is A because: {fact['fact']}"

            questions.append(
                {
                    "id": i + 1,
                    "question": question_text,
                    "options": options,
                    "correct_answer": correct_answer,
                    "explanation": explanation,
                }
            )

        return questions

    @property
    def question_db(self) -> Dict[str, Any]:
        return self._question_db

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        verified_facts = ctx.session.state.get("verified_facts", [])
        quiz = self.generate_quiz(verified_facts)
        yield Event(
            author=self.name,
            state={"quiz": quiz}
        )
