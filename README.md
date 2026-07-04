# ExamDigest 📚

> **⚠️ Simulation Notice:** ExamDigest is an **educational demonstration project**. All digest facts
> and quiz questions are generated from **mock data** and do not represent official exam
> notifications, live news, or authoritative government sources. Each fact includes a source link
> — please verify independently before relying on any information for your exam preparation.

A staged AI-agent pipeline that curates **syllabus-relevant current affairs** and generates
**practice MCQs** for competitive exam aspirants — targeting **Kerala PSC**, **SSC (CGL/CHSL)**,
and **Railway (RRB)** exams.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Staged Agent Pipeline** | 5 cleanly separated stages: Collect → Filter → Summarise → Verify → Quiz |
| **Kerala-specific Content** | Vizhinjam Port, KFON, K-Smart, Aksharasree, Kudumbashree & more |
| **Indian National Affairs** | ISRO Gaganyaan, India Semiconductor Mission, UPS, Kavach, Vande Bharat |
| **Syllabus Tag Filtering** | Articles scored against PSC / SSC / Railway keyword maps |
| **Deduplication Memory** | `seen_topics.json` prevents repeat articles across runs |
| **Source-Linked Facts** | Every fact carries a `source_url` for independent verification |
| **Interactive Quiz** | 5 MCQs with real-time scoring, explanations & grade banner |
| **Pipeline Visualisation** | Animated stage-by-stage progress in the Streamlit UI |
| **Error / Empty States** | Graceful messages when backend is down or memory is exhausted |
| **Memory Reset** | One-click reset from UI or CLI to re-run the full dataset |
| **CLI Support** | `python cli/main.py --exam psc` for developer/testing use |
| **REST API** | FastAPI backend with Swagger docs at `/docs` |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Streamlit UI (Browser)                    │
│   Exam selector → Generate button → Digest tabs → Quiz form     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP (GET /current-affairs, GET /quiz)
                           │ HTTP (POST /reset-memory)
┌──────────────────────────▼──────────────────────────────────────┐
│                    FastAPI Server  (port 8000)                   │
│              server/app.py  ·  CORS enabled                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ calls
┌──────────────────────────▼──────────────────────────────────────┐
│                   Staged Pipeline  (cli/main.py)                 │
│                                                                  │
│  ┌─────────────┐   ┌──────────────┐   ┌────────────────┐        │
│  │ 1. Collector│──▶│ 2. Rel.Filter│──▶│ 3. Summariser  │        │
│  │ (mock DB)   │   │ (syllabus    │   │ (exam-ready    │        │
│  │             │   │  tags +      │   │  facts)        │        │
│  │             │   │  dedup)      │   │                │        │
│  └─────────────┘   └──────────────┘   └───────┬────────┘        │
│                                               │                  │
│                    ┌──────────────┐   ┌───────▼────────┐        │
│                    │ 5. Quiz Gen  │◀──│ 4. Critique /  │        │
│                    │ (5 MCQs)     │   │    Verifier    │        │
│                    └──────┬───────┘   └────────────────┘        │
│                           │                                      │
│                    ┌──────▼───────┐                              │
│                    │  Memory Store│ (data/seen_topics.json)      │
│                    └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

### Pipeline Stages

| # | Stage | File | Description |
|---|-------|------|-------------|
| 1 | **News Collector** | `agents/collector.py` | Returns mock article database (20 items across PSC/SSC/Railway) |
| 2 | **Relevance Filter** | `agents/filter.py` | Matches articles to exam syllabus tags; skips seen topics |
| 3 | **Summariser** | `agents/summarizer.py` | Rewrites each article into a concise, syllabus-relevant fact |
| 4 | **Critique / Verifier** | `agents/critique.py` | Validates URL protocol, non-empty content, and minimum fact length |
| 5 | **Quiz Generator** | `agents/quiz.py` | Produces 5 MCQs mapped to digest facts, with options and explanations |

### Data Files

| File | Purpose |
|------|---------|
| `data/syllabus_tags.json` | Keyword/tag maps for PSC, SSC, and Railway syllabi |
| `data/seen_topics.json` | Memory store — tracks titles & URLs already shown |
| `outputs/digest.md` | Last generated digest in Markdown format |
| `outputs/quiz.json` | Last generated quiz in JSON format |

---

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.10+
- [`uv`](https://github.com/astral-sh/uv) package manager

### 1. Clone the repository

```bash
git clone <repo-url>
cd ExamDigest
```

### 2. Create and activate a virtual environment

```bash
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

---

## 🚀 Running Locally

You need **two terminal windows**.

### Terminal 1 — Start the FastAPI backend

```bash
uv run python -m uvicorn server.app:app --host 127.0.0.1 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.  
Interactive Swagger docs: `http://localhost:8000/docs`

### Terminal 2 — Start the Streamlit UI

```bash
uv run python -m streamlit run streamlit_app/app.py
```

Open your browser at **`http://localhost:8501`**.

---

## 💻 CLI Usage

```bash
# Run pipeline for Kerala PSC
python cli/main.py --exam psc

# Run pipeline for SSC
python cli/main.py --exam ssc

# Run pipeline for Railway
python cli/main.py --exam railway

# Clear deduplication memory (allows re-running the full dataset)
python cli/main.py --reset-memory

# Reset memory AND run the pipeline
python cli/main.py --exam psc --reset-memory
```

Output files are saved to `outputs/digest.md` and `outputs/quiz.json`.

---

## 🌐 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API info and endpoint listing |
| `GET` | `/health` | Liveness probe |
| `GET` | `/current-affairs?exam={psc\|ssc\|railway}` | Run pipeline; return digest facts |
| `GET` | `/quiz?exam={psc\|ssc\|railway}` | Run pipeline; return 5-question quiz |
| `POST` | `/reset-memory` | Clear `seen_topics.json` dedup memory |

Full interactive docs at `http://localhost:8000/docs` (Swagger UI).

---

## 📸 Screenshots

> Add screenshots of the running application here after deployment.

| View | Description |
|------|-------------|
| `screenshots/hero.png` | Home screen with exam selector |
| `screenshots/digest.png` | Study Digest tab with fact cards |
| `screenshots/quiz.png` | Practice Quiz with answer selection |
| `screenshots/score.png` | Score banner after quiz submission |

---

## 🔭 Future Improvements

- **Live News Integration** — Replace mock DB with real Google News / RSS / NewsAPI feeds
- **LLM Summarisation** — Use Gemini / GPT-4o to generate dynamic, contextualised summaries
- **Daily Scheduler** — Cron job to auto-run the pipeline and push digests via email/WhatsApp
- **User Accounts** — Personalised history, bookmarks, and streak tracking
- **Multilingual Support** — Digest and quiz output in Malayalam, Hindi, Tamil
- **Difficulty Levels** — Beginner / Intermediate / Advanced MCQ tiers
- **Exam Calendar Integration** — Tag facts with upcoming exam dates for urgency weighting
- **Offline Mode** — PWA-compatible Streamlit build for low-connectivity users
- **Analytics Dashboard** — Per-topic accuracy trends and study-time tracking
- **Production Deployment** — Streamlit Cloud + Cloud Run containerised backend with CI/CD

---

## 📂 Project Structure

```
ExamDigest/
├── agents/
│   ├── collector.py      # Stage 1: Mock news article database
│   ├── filter.py         # Stage 2: Syllabus relevance + deduplication
│   ├── summarizer.py     # Stage 3: Exam-ready fact generation
│   ├── critique.py       # Stage 4: Quality verification
│   └── quiz.py           # Stage 5: MCQ generation
├── cli/
│   └── main.py           # CLI entrypoint (--exam, --reset-memory)
├── server/
│   └── app.py            # FastAPI REST API server
├── streamlit_app/
│   └── app.py            # Streamlit web UI
├── data/
│   ├── syllabus_tags.json # Exam-to-tags mapping
│   └── seen_topics.json   # Deduplication memory store
├── outputs/
│   ├── digest.md          # Last generated digest (Markdown)
│   └── quiz.json          # Last generated quiz (JSON)
├── requirements.txt
├── SPEC.md
└── README.md
```

---

## 📄 License

Licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
