#!/bin/sh
set -eu

# Single Railway port: Streamlit (internal) + POST /stripe-webhook (public)
export PORT="${PORT:-8501}"
export STREAMLIT_INTERNAL_PORT="${STREAMLIT_INTERNAL_PORT:-8502}"

exec python gateway.py
