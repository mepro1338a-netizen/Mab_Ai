#!/bin/sh
set -eu
export PORT="${PORT:-8501}"
exec streamlit run main.py \
  --server.port="$PORT" \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false \
  --server.enableWebsocketCompression=false \
  --server.websocketPingInterval=25 \
  --browser.gatherUsageStats=false
