#!/usr/bin/env bash
#
# run.sh – helper script to start CurioBot API + Gradio UI
#
# Usage:
#   ./run.sh api      # start FastAPI (UVicorn) only
#   ./run.sh ui       # start Gradio UI only (expects API already running)
#   ./run.sh all      # start API in background, then UI in foreground
#   ./run.sh help     # show this help
#
# Notes:
#   - Make sure you have a virtualenv active with requirements installed:
#       pip install -r requirements.txt
#   - Required env vars:
#       OPENAI_API_KEY   # for router (OpenAI)
#       NEWSAPI_KEY      # for get_news tool
#   - Optional env vars:
#       OPENAI_API_BASE  # custom OpenAI base URL
#       OPENAI_MODEL     # override default model
#       API_BASE         # for UI (defaults to http://localhost:7421)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Ensure Python can find the local packages (api/, core/, server/, etc.)
export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"

API_HOST="127.0.0.1"
API_PORT="7421"

start_api() {
  echo "Starting FastAPI (CurioBot API) on ${API_HOST}:${API_PORT}..."
  uvicorn api.main:app --host "${API_HOST}" --port "${API_PORT}" --reload
}

start_ui() {
  # Let the UI know where the API lives (if user didn't override)
  export API_BASE="${API_BASE:-http://${API_HOST}:${API_PORT}}"
  echo "Starting Gradio UI (API_BASE=${API_BASE})..."
  python gradio_app/gradio_ui.py
}

start_all() {
  echo "Starting API in background..."
  uvicorn api.main:app --host "${API_HOST}" --port "${API_PORT}" --reload &
  API_PID=$!
  echo "API PID: ${API_PID}"

  # Give API a couple of seconds to come up
  sleep 3

  # Start UI in foreground
  export API_BASE="${API_BASE:-http://${API_HOST}:${API_PORT}}"
  echo "Starting Gradio UI (API_BASE=${API_BASE})..."
  python gradio_app/gradio_ui.py

  echo "Stopping API (PID ${API_PID})..."
  kill "${API_PID}" || true
}

show_help() {
  sed -n '1,40p' "$0" | sed -n '1,40p'  # print header comments
}

CMD="${1:-all}"

case "${CMD}" in
  api)
    start_api
    ;;
  ui)
    start_ui
    ;;
  all)
    start_all
    ;;
  help|-h|--help)
    show_help
    ;;
  *)
    echo "Unknown command: ${CMD}"
    echo "Usage: $0 [api|ui|all|help]"
    exit 1
    ;;
esac
