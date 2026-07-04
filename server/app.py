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

import logging
import os
import sys
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Adjust path to import from workspace root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli.main import reset_memory, run_pipeline

# ─── Logging ────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ─── App ────────────────────────────────────────────────────────────────────

VALID_EXAMS = ["psc", "ssc", "railway"]
EXAM_LABELS = {"psc": "Kerala PSC", "ssc": "Staff Selection Commission (SSC)", "railway": "Railway (RRB)"}

app = FastAPI(
    title="ExamDigest API",
    description=(
        "FastAPI backend for ExamDigest — a simulation of a staged current-affairs "
        "digest and quiz agent for competitive exam aspirants (PSC, SSC, Railway). "
        "⚠ This is a DEMO using mock data and does not represent official exam sources."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow Streamlit (and any local frontend) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _validate_exam(exam: str) -> str:
    """Normalise and validate exam type, raising HTTP 400 on bad input."""
    exam_lower = exam.strip().lower()
    if exam_lower not in VALID_EXAMS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid exam type '{exam}'. Must be one of: {VALID_EXAMS}.",
        )
    return exam_lower


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
def read_root():
    """API entry point — lists available endpoints."""
    return {
        "service": "ExamDigest API",
        "version": "1.0.0",
        "disclaimer": (
            "⚠  SIMULATION DEMO: All digest data is generated from mock current-affairs "
            "articles for educational purposes only. This does not represent official "
            "exam authority dispatches or live news sources."
        ),
        "endpoints": {
            "GET /generate?exam={psc|ssc|railway}": "Run pipeline ONCE; return digest + quiz together (recommended).",
            "GET /current-affairs?exam={psc|ssc|railway}": "Run pipeline; return digest facts only.",
            "GET /quiz?exam={psc|ssc|railway}": "Run pipeline; return 5-question MCQ quiz only.",
            "POST /reset-memory": "Clear the deduplication memory store.",
            "GET /health": "Service health check.",
        },
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/generate", tags=["Digest"])
def generate(
    exam: str = Query(..., description="Target exam type: psc, ssc, or railway"),
):
    """
    Run the full staged-agent pipeline **once** and return both the digest
    facts and 5-question MCQ quiz in a single response.

    Use this endpoint from the UI to avoid running the pipeline twice.
    Each call also updates the seen-topics memory.
    """
    exam_lower = _validate_exam(exam)
    logger.info("Pipeline requested — exam=%s endpoint=/generate", exam_lower)

    try:
        facts, quiz = run_pipeline(exam_lower)
        return {
            "exam": exam_lower,
            "exam_label": EXAM_LABELS[exam_lower],
            "status": "success",
            "fact_count": len(facts),
            "question_count": len(quiz),
            "disclaimer": (
                "⚠  SIMULATION: Data is mock/demo content for educational purposes only."
            ),
            "digest": facts,
            "quiz": quiz,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
    except FileNotFoundError as exc:
        logger.error("Missing data file: %s", exc)
        raise HTTPException(status_code=500, detail=f"Configuration error: {exc}")
    except Exception as exc:
        logger.exception("Pipeline failed for exam=%s", exam_lower)
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {exc}")


@app.get("/health", tags=["Info"])
def health_check():
    """Simple liveness probe."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}


@app.get("/current-affairs", tags=["Digest"])
def get_current_affairs(
    exam: str = Query(..., description="Target exam type: psc, ssc, or railway"),
):
    """
    Run the full staged-agent pipeline and return the verified digest facts
    for the specified exam category.

    Each fact includes a `source_url` for independent verification.
    """
    exam_lower = _validate_exam(exam)
    logger.info("Pipeline requested — exam=%s endpoint=/current-affairs", exam_lower)

    try:
        facts, _ = run_pipeline(exam_lower)
        return {
            "exam": exam_lower,
            "exam_label": EXAM_LABELS[exam_lower],
            "status": "success",
            "fact_count": len(facts),
            "disclaimer": (
                "⚠  SIMULATION: Data is mock/demo content for educational purposes only."
            ),
            "digest": facts,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
    except FileNotFoundError as exc:
        logger.error("Missing data file: %s", exc)
        raise HTTPException(status_code=500, detail=f"Configuration error: {exc}")
    except Exception as exc:
        logger.exception("Pipeline failed for exam=%s", exam_lower)
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {exc}")


@app.get("/quiz", tags=["Quiz"])
def get_quiz(
    exam: str = Query(..., description="Target exam type: psc, ssc, or railway"),
):
    """
    Run the full staged-agent pipeline and return 5 multiple-choice questions
    based on the digest for the specified exam category.
    """
    exam_lower = _validate_exam(exam)
    logger.info("Pipeline requested — exam=%s endpoint=/quiz", exam_lower)

    try:
        _, quiz = run_pipeline(exam_lower)
        return {
            "exam": exam_lower,
            "exam_label": EXAM_LABELS[exam_lower],
            "status": "success",
            "question_count": len(quiz),
            "disclaimer": (
                "⚠  SIMULATION: Questions are generated from mock data for practice only."
            ),
            "quiz": quiz,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
    except FileNotFoundError as exc:
        logger.error("Missing data file: %s", exc)
        raise HTTPException(status_code=500, detail=f"Configuration error: {exc}")
    except Exception as exc:
        logger.exception("Pipeline failed for exam=%s", exam_lower)
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {exc}")


@app.post("/reset-memory", tags=["Admin"])
def clear_memory():
    """
    Clear the deduplication memory store (`data/seen_topics.json`).

    After calling this, the next pipeline run will include all articles again,
    allowing demonstration of the full dataset without restarts.
    """
    try:
        path = reset_memory()
        logger.info("Memory cleared: %s", path)
        return {
            "status": "success",
            "message": "Deduplication memory cleared. Next run will show all articles.",
            "cleared_file": path,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as exc:
        logger.exception("Failed to reset memory")
        raise HTTPException(status_code=500, detail=f"Could not reset memory: {exc}")
