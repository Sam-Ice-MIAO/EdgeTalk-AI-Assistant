#!/usr/bin/env bash

set -euo pipefail


PROJECT_ROOT="$(
  cd "$(dirname "$0")/.."
  pwd
)"

cd "$PROJECT_ROOT"


COMPOSE_FILE="docker-compose.pro.yml"
MODEL_PATH="models/qwen1.5b.gguf"

MAX_WAIT_SECONDS=120
WAIT_INTERVAL=5


echo
echo "EdgeTalk Pro Deployment"
echo "=================================================="


if ! command -v docker >/dev/null 2>&1; then
  echo "[ERROR] Docker not found."
  exit 1
fi


if ! command -v docker-compose >/dev/null 2>&1; then
  echo "[ERROR] docker-compose not found."
  exit 1
fi


if [ ! -f "$MODEL_PATH" ]; then
  echo "[ERROR] Local LLM model not found:"
  echo "$MODEL_PATH"
  exit 1
fi


mkdir -p reports
mkdir -p data/memory


echo "[1/4] Docker environment OK"
echo "[2/4] Starting EdgeTalk Pro..."


docker-compose \
  -f "$COMPOSE_FILE" \
  up \
  -d \
  --no-build


echo "[3/4] Waiting for API readiness..."


elapsed=0

while true; do
  status="$(
    docker inspect \
      --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' \
      edgetalk-pro-api \
      2>/dev/null \
      || true
  )"

  if [ "$status" = "healthy" ]; then
    echo "API status: healthy"
    break
  fi

  if [ "$elapsed" -ge "$MAX_WAIT_SECONDS" ]; then
    echo
    echo "[ERROR] API did not become healthy within ${MAX_WAIT_SECONDS}s."
    echo
    echo "Run:"
    echo "docker-compose -f $COMPOSE_FILE logs --tail=100 api"
    exit 1
  fi

  echo "API status: ${status:-starting} (${elapsed}s)"

  sleep "$WAIT_INTERVAL"

  elapsed=$((elapsed + WAIT_INTERVAL))
done


echo "[4/4] Warming up RAG..."


if curl \
  -fsS \
  --max-time 60 \
  -X POST \
  "http://127.0.0.1:8000/rag-chat" \
  -H "Content-Type: application/json" \
  -d '{"text":"E03报警是什么意思？"}' \
  >/dev/null
then
  echo "RAG warm-up: OK"
else
  echo "[WARNING] RAG warm-up failed."
  echo "The service is running, but the first RAG request may be slower."
fi


echo
docker-compose \
  -f "$COMPOSE_FILE" \
  ps


echo
echo "=================================================="
echo "EdgeTalk Pro is ready."
echo
echo "Web:"
echo "http://localhost:8080"
echo
echo "FastAPI:"
echo "http://localhost:8000"
echo
echo "FastAPI Docs:"
echo "http://localhost:8000/docs"
echo "=================================================="
