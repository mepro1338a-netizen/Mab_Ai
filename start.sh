#!/bin/sh
set -eu
export PORT="${PORT:-8501}"

# --- MaByte volume diagnostics (runs BEFORE python boot) --------------------
# So the very first lines in Railway logs already show whether DATA_DIR points
# to a mounted volume. If /data is missing here, no volume is attached and
# accounts will be lost on every redeploy.
_MABYTE_DATA_DIR="${DATA_DIR:-<unset>}"
if [ -d /data ]; then _MABYTE_DATA_EXISTS="yes"; else _MABYTE_DATA_EXISTS="no"; fi
if [ -w /data ] 2>/dev/null; then _MABYTE_DATA_WRITABLE="yes"; else _MABYTE_DATA_WRITABLE="no"; fi
_MABYTE_MOUNT="unknown"
if command -v mountpoint >/dev/null 2>&1; then
  if mountpoint -q /data 2>/dev/null; then _MABYTE_MOUNT="yes"; else _MABYTE_MOUNT="no"; fi
elif [ -r /proc/mounts ]; then
  if grep -qE ' /data ' /proc/mounts 2>/dev/null; then _MABYTE_MOUNT="yes"; else _MABYTE_MOUNT="no"; fi
fi
echo "[MaByte] boot DATA_DIR=${_MABYTE_DATA_DIR} /data exists=${_MABYTE_DATA_EXISTS} writable=${_MABYTE_DATA_WRITABLE} mountpoint=${_MABYTE_MOUNT} RAILWAY_ENVIRONMENT=${RAILWAY_ENVIRONMENT:-<unset>}"
if [ -n "${RAILWAY_ENVIRONMENT:-}" ] && { [ "${_MABYTE_DATA_EXISTS}" != "yes" ] || [ "${DATA_DIR:-}" != "/data" ]; }; then
  echo "[MaByte] WARN: Railway detected but /data volume is NOT mounted or DATA_DIR is not /data — accounts will be wiped on every redeploy. Fix: Railway → Service → Volumes → New Volume (Mount Path /data) + Variables → DATA_DIR=/data." >&2
fi
# ---------------------------------------------------------------------------

exec streamlit run main.py \
  --server.port="$PORT" \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false \
  --server.enableWebsocketCompression=false \
  --server.websocketPingInterval=25 \
  --browser.gatherUsageStats=false
