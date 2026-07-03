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

import os
import sys
from fastapi import FastAPI, HTTPException, Query

# Adjust path to import from workspace root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli.main import run_pipeline

app = FastAPI(
    title="Current Affairs Digest Agent API",
    description="FastAPI server for retrieving syllabus-specific current affairs and practice quizzes.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Current Affairs Digest Agent API!",
        "endpoints": {
            "/current-affairs?exam={psc|ssc|railway}": "Retrieve the daily current affairs digest for an exam.",
            "/quiz?exam={psc|ssc|railway}": "Retrieve a 5-question MCQ practice quiz based on the digest."
        }
    }

@app.get("/current-affairs")
def get_current_affairs(exam: str = Query(..., description="The target exam type: psc, ssc, or railway")):
    exam_lower = exam.lower()
    if exam_lower not in ["psc", "ssc", "railway"]:
        raise HTTPException(status_code=400, detail="Invalid exam type. Must be 'psc', 'ssc', or 'railway'.")
    
    try:
        facts, _ = run_pipeline(exam_lower)
        return {
            "exam": exam_lower,
            "status": "success",
            "digest": facts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

@app.get("/quiz")
def get_quiz(exam: str = Query(..., description="The target exam type: psc, ssc, or railway")):
    exam_lower = exam.lower()
    if exam_lower not in ["psc", "ssc", "railway"]:
        raise HTTPException(status_code=400, detail="Invalid exam type. Must be 'psc', 'ssc', or 'railway'.")
    
    try:
        _, quiz = run_pipeline(exam_lower)
        return {
            "exam": exam_lower,
            "status": "success",
            "quiz": quiz
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")
