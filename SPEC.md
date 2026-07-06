# ExamDigest: Current Affairs Digest Agent for Competitive Exam Aspirants

## 1. Problem Statement
Exam aspirants for PSC, SSC, and Railway exams need a fast, reliable way to
stay current with syllabus-relevant news and convert it into exam-ready facts
and practice questions. Today they must manually scan multiple news sources,
filter relevance, and rewrite information into study-friendly form.

**Persona:** A competitive exam aspirant who wants a daily, verified current
affairs summary plus a short quiz without spending hours reading raw news.

## 2. Project Goal
Build a Streamlit web application as the primary interface, supported by a secondary CLI driver for developer testing, that produces a current affairs digest and quiz for a selected exam category. The first version defaults to deterministic mock data for reliable demos and tests, with an opt-in free live-source mode.

A successful run of the application (Streamlit or `python main.py --exam psc` / `ssc` / `railway`) should:
- Generate a dated digest of up to 8-12 relevant current affairs items, using available verified items when live public sources return fewer results
- Format each item as a concise exam-style fact with an explicit source URL
- Produce 5 multiple-choice questions based on the digest with an answer key
- Avoid duplicate topics from the recent history (memory-backed dedupe)
- Ensure every digest fact remains traceable to a real source

## 3. Architecture Overview
The system uses a staged agent workflow with clearly separated responsibilities.

- **Streamlit Web UI**: A web interface that allows users to choose an exam type and displays the generated study digest and quiz.
- **FastAPI Server**: The backend API server that exposes endpoints to trigger pipeline stages and fetch results.
- **News Collector**: Stage 1 agent that returns mock article data by default, or free live-source results in live mode.
- **Relevance Filter**: Stage 2 agent that matches articles to exam syllabus tags and filters out seen topics.
- **Summarizer**: Stage 3 agent that rewrites each selected article into a concise, syllabus-relevant fact.
- **Critique / Verifier**: Stage 4 agent that checks digest facts against source URLs and verifies faithfulness.
- **Quiz Generator**: Stage 5 agent that produces 5 MCQs mapped to digest facts.
- **Memory Store**: Tracks seen topics to prevent repeats across runs.

This design decouples retrieval, filtering, rewriting, question generation, and
verification so each stage can be tuned independently.

## 4. Tools and Data
- Search/Collector tool: deterministic mock data for default mode; GDELT search queries (and optional RSS feeds configured in `data/source_config.json`) for live mode. **If `GEMINI_API_KEY` is absent, the system runs fully offline using mock Gemini client fallback.**
- Static syllabus map: JSON-based keyword/tag definitions for PSC, SSC, and
  Railway syllabus topics
- Static source map: JSON-based live-source query definitions for PSC, SSC, and
  Railway topics
- File-backed memory: JSON (or SQLite) storage for seen topics and run history
- Web App UI: Streamlit application as the primary user interface
- CLI entrypoint: `main.py` with `--exam` argument for testing/debugging and local outputs

## 5. Constraints
- Primary deliverable is the Streamlit Web UI; the CLI remains supported as a secondary tool for testing/debugging
- Keep LLM usage efficient: batch-process items instead of one call per article
- Use the lowest-cost available model or free-tier option for prompt stages
- Cache raw search results in development to minimize repeated external calls
- Live mode must remain best-effort and free; no API keys or paid news APIs are
  required for the first version
- Do not rely on model fine-tuning; use prompt design, structured tools, and
  verification logic instead

## 6. Non-Goals
- No authentication, user accounts, or personalization beyond exam type
- No mobile app or push notification system
- No guarantee of perfect factual accuracy; every item must include a source
  link so the user can verify claims
- No production-grade deployment in the first version; focus on local/cloud demo

## 7. Success Criteria
- The project runs end-to-end from mock/live collection to digest and quiz
- Digest items are relevant, concise, and linked to real sources
- Quiz questions are generated from the digest content
- Recent-topic memory prevents repeated topics across multiple runs
- Judges can interact with the app in the browser and verify the CLI outputs match the generated digest and quiz contents
- The writeup or demo clearly explains the staged agent workflow and
  verification process

## 8. Deliverables for the First Capstone Submission
- `streamlit_app/app.py` for the Streamlit web application
- `server/app.py` for the FastAPI backend server
- `main.py` root CLI driver with `--exam` selection for developer testing
- `cli/main.py` module entrypoint that exposes the same CLI flow
- `data/syllabus_tags.json` for PSC, SSC, Railway topic filtering
- `data/source_config.json` for free live-source query configuration
- `data/seen_topics.json` or equivalent memory store
- Output files `outputs/digest.md` and `outputs/quiz.json`
- Project documentation (`README.md`, `SPEC.md`, `ARCHITECTURE.md`) documenting the architecture, tools, and verification strategy

## 9. Installation
For detailed installation and setup instructions, please see [README.md](README.md).

## 10. Run Instructions
To run the system locally, use the provided launcher script from the project root:

```bash
./run.sh
```

On Windows, run:

```bat
run.bat
```

The launcher starts the FastAPI backend and the Streamlit UI together, exposing:
- `http://localhost:8000` for the API and docs
- `http://localhost:8501` for the UI

Choose the target exam category, and click the generate button to fetch the latest digest and quiz.

If you prefer to start the services manually, you can still run them separately:
```bash
uv run python -m uvicorn server.app:app --host 127.0.0.1 --port 8000
uv run python -m streamlit run streamlit_app/app.py
```

To run live free-source mode from the CLI:
```bash
python cli/main.py --exam psc --data-mode live
```

To run live free-source mode from the API:
```bash
curl "http://localhost:8000/generate?exam=psc&data_mode=live"
```

## 11. Documentation Maintenance
- Update the README and SPEC whenever the CLI entrypoints, file layout, or runtime behavior change.
- A CI workflow runs a lightweight documentation verification script so drift is caught on pull requests and pushes.
