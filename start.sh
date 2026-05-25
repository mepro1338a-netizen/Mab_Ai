#!/bin/sh
set -eu
export PORT="${PORT:-8080}"
export STREAMLIT_INTERNAL_PORT="${STREAMLIT_INTERNAL_PORT:-8502}"
exec python gateway.py
