#!/bin/sh
set -eu

PORT="${PORT:-8501}"

exec streamlit run main.py \
  --server.port="${PORT}" \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.gatherUsageStats=false
