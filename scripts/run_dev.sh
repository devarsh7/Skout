#!/usr/bin/env bash
# Dev runner (macOS/Linux). For Windows, use scripts/run_dev.bat.
set -euo pipefail

cd "$(dirname "$0")/.."

# 1. Ensure Ollama is reachable
if ! curl -sf http://localhost:11434/api/tags >/dev/null; then
  echo "⚠️  Ollama doesn't seem to be running at :11434."
  echo "   Start it with: ollama serve   (and: ollama pull llama3.1:8b)"
fi

# 2. Activate venv if it exists
if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

# 3. Start FastAPI in background
echo "🚀 Starting FastAPI on :8000"
uvicorn backend.main:app --reload --port 8000 &
FASTAPI_PID=$!
trap "kill $FASTAPI_PID 2>/dev/null || true" EXIT

sleep 2

# 4. Start Streamlit (foreground)
echo "🎨 Starting Streamlit on :8501"
PYTHONPATH="$(pwd)" streamlit run frontend/streamlit_app.py
