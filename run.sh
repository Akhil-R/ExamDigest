#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

cleanup() {
  trap - EXIT INT TERM
  if [[ -n "${BACKEND_PID:-}" ]]; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
  if [[ -n "${STREAMLIT_PID:-}" ]]; then
    kill "$STREAMLIT_PID" 2>/dev/null || true
  fi
  wait "$BACKEND_PID" 2>/dev/null || true
  wait "$STREAMLIT_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "Starting ExamDigest backend..."
uv run python -m uvicorn server.app:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

echo "Starting ExamDigest Streamlit UI..."
uv run python -m streamlit run streamlit_app/app.py &
STREAMLIT_PID=$!

echo
printf 'Backend: http://localhost:8000\n'
printf 'UI: http://localhost:8501\n'
echo
printf 'Press Ctrl+C to stop both services.\n'

wait -n "$BACKEND_PID" "$STREAMLIT_PID"
