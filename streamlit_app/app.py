
"""ExamDigest — Streamlit Web Application.

Primary user interface for the Current Affairs Digest Agent.
Communicates with the FastAPI backend to run the staged pipeline and
render digest facts and MCQ quizzes in a rich, responsive dashboard.
"""

import json
import os
import time

import requests
import streamlit as st

# ─── Page Config (must be first Streamlit call) ───────────────────────────────

st.set_page_config(
    page_title="ExamDigest — Current Affairs for Exam Aspirants",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/",
        "Report a bug": "https://github.com/",
        "About": "ExamDigest: A simulation of a staged AI agent that produces current-affairs digests and quizzes for PSC, SSC, and Railway exam aspirants.",
    },
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown(
    """
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.main { background: #0d1117; }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; }

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, #1a1f35 0%, #0f2027 50%, #1a3a4a 100%);
    border: 1px solid #2d4a6a;
    border-radius: 16px;
    padding: 2.2rem 2.5rem;
    margin-bottom: 1.5rem;
}
.hero-banner h1 {
    color: #e2e8f0;
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 0.4rem 0;
}
.hero-banner p {
    color: #94a3b8;
    font-size: 1rem;
    margin: 0;
    line-height: 1.6;
}
.hero-badge {
    display: inline-block;
    background: rgba(59,130,246,0.15);
    border: 1px solid #3b82f6;
    color: #60a5fa;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    padding: 3px 12px;
    margin-bottom: 0.9rem;
}

/* ── Disclaimer ── */
.disclaimer-box {
    background: rgba(234, 179, 8, 0.08);
    border: 1px solid rgba(234, 179, 8, 0.35);
    border-left: 4px solid #eab308;
    border-radius: 8px;
    padding: 0.8rem 1.1rem;
    margin-bottom: 1.5rem;
    color: #fde68a;
    font-size: 0.82rem;
    line-height: 1.5;
}
.disclaimer-box strong { color: #fbbf24; }

/* ── Fact Card ── */
.fact-card {
    background: linear-gradient(145deg, #161b27 0%, #1a2332 100%);
    border: 1px solid #2a3a52;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.1rem;
    transition: border-color 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}
.fact-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, #3b82f6, #06b6d4);
    border-radius: 4px 0 0 4px;
}
.fact-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 4px 24px rgba(59,130,246,0.12);
}
.fact-card h4 {
    color: #e2e8f0;
    font-size: 0.98rem;
    font-weight: 600;
    margin: 0 0 0.6rem 0;
}
.fact-card p {
    color: #94a3b8;
    font-size: 0.87rem;
    margin: 0 0 0.8rem 0;
    line-height: 1.6;
}
.fact-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #3b82f6, #06b6d4);
    color: white;
    font-weight: 700;
    font-size: 0.7rem;
    width: 22px; height: 22px;
    border-radius: 50%;
    margin-right: 0.5rem;
    flex-shrink: 0;
}
.fact-header { display: flex; align-items: flex-start; gap: 0.4rem; }

/* ── Tag Pills ── */
.tag-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 0.6rem; }
.tag-pill {
    background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.3);
    color: #93c5fd;
    border-radius: 20px;
    font-size: 0.7rem;
    padding: 2px 10px;
    font-weight: 500;
}

/* ── Source Link ── */
.source-link {
    font-size: 0.75rem;
    color: #06b6d4;
    text-decoration: none;
}
.source-link:hover { text-decoration: underline; }

/* ── Pipeline Stage ── */
.stage-row {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.45rem 0.8rem;
    border-radius: 8px;
    font-size: 0.85rem;
    color: #94a3b8;
    margin-bottom: 4px;
}
.stage-row.done {
    background: rgba(34,197,94,0.08);
    color: #86efac;
    border: 1px solid rgba(34,197,94,0.2);
}
.stage-row.running {
    background: rgba(59,130,246,0.1);
    color: #93c5fd;
    border: 1px solid rgba(59,130,246,0.25);
    animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

/* ── Quiz Card ── */
.quiz-q-header {
    color: #e2e8f0;
    font-size: 0.97rem;
    font-weight: 600;
    margin-bottom: 0.8rem;
    line-height: 1.5;
}
.quiz-q-num {
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    color: white;
    font-weight: 700;
    font-size: 0.7rem;
    border-radius: 20px;
    padding: 2px 10px;
    margin-right: 0.5rem;
}

/* ── Score Banner ── */
.score-banner {
    background: linear-gradient(135deg, #064e3b, #065f46);
    border: 1px solid #10b981;
    border-radius: 12px;
    padding: 1.2rem 1.6rem;
    text-align: center;
    margin-top: 1.5rem;
}
.score-banner h2 { color: #6ee7b7; margin: 0 0 0.4rem; font-size: 1.6rem; }
.score-banner p { color: #a7f3d0; margin: 0; font-size: 0.9rem; }

/* ── Empty State ── */
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #475569;
}
.empty-state .emoji { font-size: 3.5rem; margin-bottom: 1rem; }
.empty-state h3 { color: #64748b; font-weight: 600; margin-bottom: 0.5rem; }
.empty-state p { font-size: 0.88rem; line-height: 1.6; }

/* ── Error Box ── */
.error-box {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.35);
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    padding: 1rem 1.3rem;
    color: #fca5a5;
    font-size: 0.85rem;
    line-height: 1.6;
}
.error-box strong { color: #f87171; }
.error-box code {
    background: rgba(255,255,255,0.06);
    border-radius: 4px;
    padding: 2px 6px;
    font-family: 'Fira Code', monospace;
    font-size: 0.8rem;
    color: #fcd34d;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0d1117;
    border-right: 1px solid #1e2d3d;
}
section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    border-bottom: 1px solid #1e2d3d;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    font-size: 0.88rem;
    padding: 0.5rem 1.2rem;
    border-radius: 8px 8px 0 0;
    color: #64748b;
}
.stTabs [aria-selected="true"] {
    color: #60a5fa !important;
    background: rgba(59,130,246,0.08) !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.2s;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #0891b2);
    border: none;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1d4ed8, #0e7490);
    box-shadow: 0 4px 16px rgba(37,99,235,0.4);
    transform: translateY(-1px);
}

/* ── Select/Input ── */
.stSelectbox label, .stTextInput label {
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}

/* ── Divider ── */
hr { border-color: #1e2d3d !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ─── Constants ────────────────────────────────────────────────────────────────

EXAM_META = {
    "psc": {
        "label": "Kerala PSC",
        "icon": "🏛️",
        "colour": "#3b82f6",
        "description": "Kerala Public Service Commission — State governance, Federalism & Public Administration",
    },
    "ssc": {
        "label": "SSC (CGL/CHSL)",
        "icon": "📖",
        "colour": "#a855f7",
        "description": "Staff Selection Commission — History, Geography, Polity, Science & Economy",
    },
    "railway": {
        "label": "Railway (RRB)",
        "icon": "🚂",
        "colour": "#06b6d4",
        "description": "Railway Recruitment Board — Transportation, Railway History & General Science",
    },
}

PIPELINE_STAGES = [
    ("🔍", "News Collection", "Gathering relevant current affairs articles"),
    ("🏷️", "Relevance Filtering & Deduplication", "Scoring articles against syllabus tags"),
    ("✍️", "Fact Summarisation", "Rewriting items as concise exam-ready facts"),
    ("🔎", "Quality Verification", "Checking source links and fact quality"),
    ("❓", "Quiz Generation", "Generating 5 multiple-choice questions"),
]

# ─── Session State Init ───────────────────────────────────────────────────────

for key, default in [
    ("digest_data", None),
    ("quiz_data", None),
    ("exam_type", "psc"),
    ("data_mode", "mock"),
    ("source_warnings", []),
    ("error_msg", None),
    ("pipeline_done", False),
    ("quiz_answers", {}),
    ("quiz_submitted", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    backend_url = st.text_input(
        "Backend API URL",
        value="http://localhost:8000",
        help="URL of the running FastAPI server",
        key="backend_url",
    )

    data_mode_choice = st.selectbox(
        "Data source",
        options=["mock", "live"],
        format_func=lambda value: "Mock demo data" if value == "mock" else "Live free sources",
        index=["mock", "live"].index(st.session_state.data_mode),
        help="Mock is deterministic for demos. Live uses free public sources and may return fewer items.",
        key="data_mode_select",
    )

    st.markdown("---")
    st.markdown("### 🧠 Deduplication Memory")

    # Live memory count from local file
    _seen_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "seen_topics.json"
    )
    try:
        with open(_seen_path) as _f:
            _seen = json.load(_f)
        _seen_count = len(_seen) // 2  # titles + urls stored as pairs
    except Exception:
        _seen_count = 0

    st.markdown(
        f"<div style='background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);"
        f"border-radius:8px;padding:0.5rem 0.8rem;margin-bottom:0.7rem;'>"
        f"<span style='color:#93c5fd;font-size:0.75rem;font-weight:600;'>ARTICLES SEEN</span><br>"
        f"<span style='color:#e2e8f0;font-size:1.3rem;font-weight:700;'>{_seen_count}</span>"
        f"<span style='color:#64748b;font-size:0.75rem;'> / 20 total</span>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<span style='color:#64748b;font-size:0.8rem;'>"
        "The pipeline skips articles already seen. Reset to show all 20 again."
        "</span>",
        unsafe_allow_html=True,
    )

    if st.button("🔄 Reset Memory", use_container_width=True, help="Clear seen_topics.json"):
        try:
            resp = requests.post(f"{backend_url}/reset-memory", timeout=5)
            if resp.status_code == 200:
                st.success("✅ Memory cleared! Next run will show all 20 articles.")
                st.session_state.digest_data = None
                st.session_state.quiz_data = None
                st.session_state.pipeline_done = False
                st.session_state.error_msg = None
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.rerun()
            else:
                st.error(f"Reset failed: {resp.text}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot reach backend — is the server running?")

    st.markdown("---")
    st.markdown("### 📡 Pipeline Stages")
    for icon, name, _ in PIPELINE_STAGES:
        st.markdown(
            f"<div style='font-size:0.8rem;color:#475569;padding:3px 0;'>"
            f"{icon} {name}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.72rem;color:#374151;text-align:center;'>"
        "ExamDigest v1.0 · Educational Demo<br>"
        "Built with Streamlit + FastAPI"
        "</div>",
        unsafe_allow_html=True,
    )


# ─── Hero Banner ─────────────────────────────────────────────────────────────

st.markdown(
    """
<div class="hero-banner">
  <div class="hero-badge">SIMULATION DEMO · AI-POWERED STUDY TOOL</div>
  <h1>📚 ExamDigest</h1>
  <p>
    A staged AI agent pipeline that curates <strong>syllabus-relevant current affairs</strong>
    and generates <strong>practice MCQs</strong> for PSC, SSC &amp; Railway exam aspirants.
    Select your exam, run the pipeline, and study smarter.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

# ─── Disclaimer ───────────────────────────────────────────────────────────────

st.markdown(
    """
<div class="disclaimer-box">
  ⚠️ <strong>Simulation Notice:</strong> ExamDigest is an educational demonstration project.
  All digest facts and quiz questions are generated from <strong>mock data</strong> and do
  <strong>not</strong> represent official exam notifications, live news, or authoritative
  sources. Each fact includes a source link — please verify independently before relying on
  any information for your exam preparation.
</div>
""",
    unsafe_allow_html=True,
)

# ─── Exam Selection & Generate ────────────────────────────────────────────────

col_sel, col_btn = st.columns([3, 1], gap="medium")

with col_sel:
    exam_choice = st.selectbox(
        "🎯 Select your target exam:",
        options=list(EXAM_META.keys()),
        format_func=lambda k: f"{EXAM_META[k]['icon']}  {EXAM_META[k]['label']}",
        index=list(EXAM_META.keys()).index(st.session_state.exam_type),
        key="exam_select",
    )
    # Show description beneath
    meta = EXAM_META[exam_choice]
    st.markdown(
        f"<span style='font-size:0.8rem;color:#64748b;'>{meta['description']}</span>",
        unsafe_allow_html=True,
    )

with col_btn:
    st.markdown("<div style='height:1.55rem'></div>", unsafe_allow_html=True)  # align
    generate_btn = st.button(
        "🚀 Generate Digest & Quiz",
        type="primary",
        use_container_width=True,
    )

st.markdown("---")


# ─── Pipeline Execution ───────────────────────────────────────────────────────

def fetch_with_progress(exam: str, backend: str, data_mode: str) -> None:
    """Call /generate once to get both digest and quiz in a single pipeline run.
    
    Using a single endpoint prevents the deduplication memory from being updated
    between the digest and quiz fetches (which would cause the quiz to run on a
    different — possibly empty — set of facts).
    """
    st.session_state.exam_type = exam
    st.session_state.data_mode = data_mode
    st.session_state.error_msg = None
    st.session_state.digest_data = None
    st.session_state.quiz_data = None
    st.session_state.source_warnings = []
    st.session_state.pipeline_done = False
    st.session_state.quiz_answers = {}
    st.session_state.quiz_submitted = False

    stage_placeholder = st.empty()

    def render_stages(current: int, done: bool = False) -> None:
        rows = ""
        for i, (icon, name, _) in enumerate(PIPELINE_STAGES):
            if i < current:
                rows += f'<div class="stage-row done">✅ {name}</div>'
            elif i == current and not done:
                rows += f'<div class="stage-row running">⏳ {icon} {name} …</div>'
            else:
                rows += f'<div class="stage-row">⬜ {icon} {name}</div>'
        stage_placeholder.markdown(rows, unsafe_allow_html=True)

    try:
        # Animate stage-by-stage while the single backend call runs
        for stage_idx in range(len(PIPELINE_STAGES)):
            render_stages(stage_idx)
            time.sleep(0.45)

        render_stages(len(PIPELINE_STAGES), done=True)

        # Single /generate call — runs the pipeline exactly once and returns
        # both digest and quiz, so memory is only updated once.
        resp = requests.get(
            f"{backend}/generate",
            params={"exam": exam, "data_mode": data_mode},
            timeout=30,
        )
        if resp.status_code == 200:
            body = resp.json()
            st.session_state.digest_data = body.get("digest", [])
            st.session_state.quiz_data = body.get("quiz", [])
            st.session_state.source_warnings = body.get("source_warnings", [])
        else:
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text
            st.session_state.error_msg = f"API error ({resp.status_code}): {detail}"
            return

        st.session_state.pipeline_done = True

    except requests.exceptions.ConnectionError:
        stage_placeholder.empty()
        st.session_state.error_msg = "CONNECTION_ERROR"
    except requests.exceptions.Timeout:
        stage_placeholder.empty()
        st.session_state.error_msg = "The backend took too long to respond. Please try again."
    except Exception as exc:
        stage_placeholder.empty()
        st.session_state.error_msg = f"Unexpected error: {exc}"


if generate_btn:
    with st.spinner(""):
        fetch_with_progress(exam_choice, backend_url, data_mode_choice)
    st.rerun()

# ─── Error State ──────────────────────────────────────────────────────────────

if st.session_state.error_msg:
    if st.session_state.error_msg == "CONNECTION_ERROR":
        st.markdown(
            f"""
<div class="error-box">
  <strong>❌ Cannot Connect to Backend</strong><br><br>
  Could not reach the FastAPI server at <code>{backend_url}</code>.<br><br>
  <strong>To start the server, run:</strong><br>
  <code>uv run python -m uvicorn server.app:app --host 127.0.0.1 --port 8000 --reload</code><br><br>
  Then refresh this page and try again.
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="error-box"><strong>❌ Error:</strong> {st.session_state.error_msg}</div>',
            unsafe_allow_html=True,
        )

# ─── Empty State ──────────────────────────────────────────────────────────────

elif st.session_state.digest_data is None and not generate_btn:
    st.markdown(
        """
<div class="empty-state">
  <div class="emoji">📋</div>
  <h3>No digest generated yet</h3>
  <p>
    Select your target exam above and click <strong>Generate Digest & Quiz</strong>
    to run the AI pipeline. The app will collect relevant current affairs,
    filter and verify each item, then generate a 5-question practice quiz.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

# ─── Empty-Memory State ───────────────────────────────────────────────────────

elif st.session_state.digest_data == [] and st.session_state.pipeline_done:
    st.markdown(
        """
<div class="empty-state">
  <div class="emoji">🔁</div>
  <h3>All articles already seen!</h3>
  <p>
    The deduplication memory has filtered out all available articles for this exam category.
    Click <strong>Reset Memory</strong> in the sidebar to clear the memory and run again.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

# ─── Results: Digest + Quiz Tabs ─────────────────────────────────────────────

elif st.session_state.pipeline_done and st.session_state.digest_data is not None:
    exam_meta = EXAM_META.get(st.session_state.exam_type, {})
    facts = st.session_state.digest_data or []
    quiz = st.session_state.quiz_data or []

    st.markdown(
        f"<h3 style='color:#e2e8f0;margin-bottom:0.2rem;'>"
        f"{exam_meta.get('icon','📋')} Results — {exam_meta.get('label', st.session_state.exam_type.upper())}"
        f"</h3>"
        f"<p style='color:#64748b;font-size:0.82rem;margin-bottom:1rem;'>"
        f"Pipeline complete · {st.session_state.data_mode.title()} mode · {len(facts)} facts · {len(quiz)} questions</p>",
        unsafe_allow_html=True,
    )

    if st.session_state.source_warnings:
        st.warning(
            "Live source data was degraded or partial; showing available cached or fallback results. "
            + " | ".join(st.session_state.source_warnings[:3])
        )

    summary_cols = st.columns([2, 2, 2], gap="small")
    with summary_cols[0]:
        st.markdown(
            f"<div style='background:rgba(59,130,246,0.10);border:1px solid rgba(59,130,246,0.25);border-radius:10px;padding:0.9rem 1rem;margin-bottom:0.7rem;'>"
            f"<div style='color:#93c5fd;font-size:0.75rem;font-weight:700;'>EXAM FOCUS</div>"
            f"<div style='color:#e2e8f0;font-size:1rem;font-weight:600;margin-top:0.2rem;'>{exam_meta.get('label', 'Selected exam')}</div>"
            f"<div style='color:#64748b;font-size:0.8rem;margin-top:0.2rem;'>{exam_meta.get('description', '')}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with summary_cols[1]:
        st.markdown(
            f"<div style='background:rgba(34,197,94,0.10);border:1px solid rgba(34,197,94,0.25);border-radius:10px;padding:0.9rem 1rem;margin-bottom:0.7rem;'>"
            f"<div style='color:#86efac;font-size:0.75rem;font-weight:700;'>FACTS READY</div>"
            f"<div style='color:#e2e8f0;font-size:1.3rem;font-weight:700;margin-top:0.2rem;'>{len(facts)}</div>"
            f"<div style='color:#64748b;font-size:0.8rem;margin-top:0.2rem;'>Verified, source-linked study points</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with summary_cols[2]:
        st.markdown(
            f"<div style='background:rgba(168,85,247,0.10);border:1px solid rgba(168,85,247,0.25);border-radius:10px;padding:0.9rem 1rem;margin-bottom:0.7rem;'>"
            f"<div style='color:#d8b4fe;font-size:0.75rem;font-weight:700;'>QUIZ READY</div>"
            f"<div style='color:#e2e8f0;font-size:1.3rem;font-weight:700;margin-top:0.2rem;'>{len(quiz)}</div>"
            f"<div style='color:#64748b;font-size:0.8rem;margin-top:0.2rem;'>Practice questions with explanations</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

    tab_digest, tab_quiz = st.tabs(["📖  Study Digest", "✍️  Practice Quiz"])

    # ── Digest Tab ────────────────────────────────────────────────────────────
    with tab_digest:
        facts = st.session_state.digest_data
        if not facts:
            st.info("No facts to display. Reset memory and try again.")
        else:
            st.markdown(
                f"<p style='color:#64748b;font-size:0.85rem;margin-bottom:1rem;'>"
                f"Showing <strong style='color:#93c5fd;'>{len(facts)}</strong> verified current-affairs items "
                f"for <strong style='color:#93c5fd;'>{exam_meta.get('label','')}</strong>. "
                f"Each item includes a source link for independent verification.</p>",
                unsafe_allow_html=True,
            )
            for i, item in enumerate(facts, 1):
                tags_html = "".join(
                    f'<span class="tag-pill">{tag}</span>' for tag in item.get("tags", [])
                )
                st.markdown(
                    f"""
<div class="fact-card">
  <div class="fact-header">
    <span class="fact-number">{i}</span>
    <h4>{item['title']}</h4>
  </div>
  <p>{item['fact']}</p>
  <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;'>
    <a href="{item['source_url']}" target="_blank" class="source-link">🔗 View Source →</a>
    <span style='color:#64748b;font-size:0.74rem;'>Exam relevance: {', '.join(item.get('tags', [])[:2])}</span>
  </div>
  <div class="tag-row">{tags_html}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

    # ── Quiz Tab ──────────────────────────────────────────────────────────────
    with tab_quiz:
        quiz = st.session_state.quiz_data or []
        if not quiz:
            st.info("No quiz questions available.")
        else:
            st.markdown(
                "<p style='color:#64748b;font-size:0.85rem;margin-bottom:1.5rem;'>"
                "Answer all 5 questions and click <strong>Submit Quiz</strong> to see your score "
                "and detailed explanations.</p>",
                unsafe_allow_html=True,
            )

            with st.form("quiz_form"):
                for q in quiz:
                    qid = q["id"]
                    st.markdown(
                        f'<div class="quiz-q-header">'
                        f'<span class="quiz-q-num">Q{qid}</span>'
                        f'{q["question"]}'
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    choice = st.radio(
                        f"Select answer for Q{qid}",
                        options=q["options"],
                        key=f"quiz_q_{qid}",
                        label_visibility="collapsed",
                    )
                    st.session_state.quiz_answers[qid] = choice
                    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

                submitted = st.form_submit_button(
                    "✅ Submit Quiz", type="primary", use_container_width=False
                )
                if submitted:
                    st.session_state.quiz_submitted = True

            # ── Results after submission ──────────────────────────────────
            if st.session_state.quiz_submitted:
                score = 0
                st.markdown("---")
                st.markdown(
                    "<h4 style='color:#e2e8f0;margin-bottom:1rem;'>📊 Answer Review</h4>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    "<p style='color:#64748b;font-size:0.84rem;margin-bottom:1rem;'>"
                    "Review your answers and read the explanations to reinforce the most important study points.</p>",
                    unsafe_allow_html=True,
                )

                for q in quiz:
                    qid = q["id"]
                    user_ans = st.session_state.quiz_answers.get(qid, "")
                    correct = q["correct_answer"]
                    is_correct = user_ans == correct

                    if is_correct:
                        score += 1
                        result_colour = "#22c55e"
                        result_icon = "✅"
                        result_label = "Correct"
                    else:
                        result_colour = "#ef4444"
                        result_icon = "❌"
                        result_label = "Incorrect"

                    with st.expander(
                        f"{result_icon} Q{qid}: {q['question'][:70]}…"
                    ):
                        st.markdown(
                            f"**Your answer:** <span style='color:{result_colour};'>{user_ans}</span>",
                            unsafe_allow_html=True,
                        )
                        if not is_correct:
                            st.markdown(
                                f"**Correct answer:** <span style='color:#22c55e;'>{correct}</span>",
                                unsafe_allow_html=True,
                            )
                        st.markdown(f"**Explanation:** {q['explanation']}")

                # Score banner
                pct = int(score / len(quiz) * 100)
                grade = (
                    "🏆 Excellent!" if pct >= 80
                    else "👍 Good effort!" if pct >= 60
                    else "📚 Keep studying!"
                )
                st.markdown(
                    f"""
<div class="score-banner">
  <h2>{score}/{len(quiz)}</h2>
  <p>Score: {pct}% &nbsp;·&nbsp; {grade}</p>
</div>
""",
                    unsafe_allow_html=True,
                )
