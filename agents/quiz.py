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

class QuizGenerator:
    """Mock Quiz Generator stage.
    
    Generates 5 multiple-choice questions based on final verified digest facts.
    """
    def generate_quiz(self, facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generates a list of 5 multiple choice questions from digest facts."""
        print(f"[QuizGenerator] Generating 5 MCQs based on {len(facts)} digest facts.")
        
        questions = []
        # We need to generate exactly 5 questions.
        # If we have facts, we can base questions on them. If not, generate generic ones.
        for i in range(5):
            fact_index = i % len(facts) if facts else None
            if fact_index is not None:
                fact = facts[fact_index]
                question_text = f"Which of the following is correct regarding '{fact['title']}'?"
                options = [
                    f"It relates to: {fact['fact'][:60]}...",
                    "It has no relevance to competitive exams.",
                    "It was declared unconstitutional by all global courts.",
                    "It only affects private enterprise and has no government scope."
                ]
                correct_answer = options[0]
                explanation = f"Based on the digest, the correct option is A because: {fact['fact']}"
            else:
                question_text = f"Sample current affairs question {i + 1}?"
                options = ["Option A", "Option B", "Option C", "Option D"]
                correct_answer = "Option A"
                explanation = "Option A is correct based on general knowledge."
                
            questions.append({
                "id": i + 1,
                "question": question_text,
                "options": options,
                "correct_answer": correct_answer,
                "explanation": explanation
            })
            
        return questions
