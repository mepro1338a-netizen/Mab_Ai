#!/bin/sh
set -eu
export PORT="${PORT:-8000}"
exec uvicorn api.app:app --host 0.0.0.0 --port "$PORT"
