#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d .venv ]; then python3 -m venv .venv; fi
.venv/bin/python -m pip install -q -r requirements.txt
mkdir -p runtime
if [ ! -f runtime/finn.db ] && [ -f data/seed_cache.db ]; then cp data/seed_cache.db runtime/finn.db; fi
exec .venv/bin/python -m uvicorn backend.app:app --host "${FINN_HOST:-127.0.0.1}" --port "${PORT:-8000}"
