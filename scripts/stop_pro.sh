#!/usr/bin/env bash

set -euo pipefail


PROJECT_ROOT="$(
  cd "$(dirname "$0")/.."
  pwd
)"

cd "$PROJECT_ROOT"


echo
echo "Stopping EdgeTalk Pro..."
echo


docker-compose \
  -f docker-compose.pro.yml \
  down


echo
echo "EdgeTalk Pro stopped."
