#!/bin/sh
set -eu
# Railway production — MUST use gateway (Stripe webhook + Streamlit proxy)
export PORT="${PORT:-8501}"
export STREAMLIT_INTERNAL_PORT="${STREAMLIT_INTERNAL_PORT:-8502}"
exec python gateway.py
