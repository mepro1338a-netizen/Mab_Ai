#!/usr/bin/env python3
"""MaByte DB persistence check — is the SQLite file on a persistent volume?

Prints DATA_DIR, DB_PATH, file existence, size, user count, and a Railway
volume heuristic. Never prints passwords or DB rows.

Usage:
  python tools/db_status.py
  railway run python tools/db_status.py
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse resolution (same rules as config.py) without pulling in the whole app.
from tools.db_migrate import default_data_dir, default_db_path  # noqa: E402


def _on_railway() -> bool:
    return bool(
        os.getenv("RAILWAY_ENVIRONMENT")
        or os.getenv("RAILWAY_PROJECT_ID")
        or os.getenv("RAILWAY_SERVICE_ID")
    )


def _looks_ephemeral(data_dir: Path) -> bool:
    s = str(data_dir)
    return not (s == "/data" or s.startswith("/data/"))


def _write_test(data_dir: Path) -> tuple[bool, str]:
    probe = data_dir / ".mabyte_write_probe"
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True, ""
    except OSError as exc:
        return False, str(exc)


def _user_count(db_path: Path) -> int | None:
    if not db_path.is_file():
        return None
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        try:
            row = conn.execute("SELECT COUNT(*) FROM users").fetchone()
            return int(row[0]) if row else 0
        finally:
            conn.close()
    except sqlite3.Error:
        return None


def _fmt_size(n: int) -> str:
    return f"{n:,} bytes ({n / 1024:.1f} KiB)" if n else "0 bytes"


def _fmt_mtime(ts: float) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(ts))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report where MaByte's SQLite DB lives and whether writes persist."
    )
    parser.add_argument("--db", default=None, help="SQLite file (default: DATA_DIR/mabai.db)")
    args = parser.parse_args()

    data_dir = default_data_dir()
    db_path = Path(args.db).resolve() if args.db else default_db_path()

    env_data_dir = os.getenv("DATA_DIR", "").strip() or "(unset)"
    on_railway = _on_railway()
    ephemeral = _looks_ephemeral(data_dir)
    writable, write_err = _write_test(data_dir)

    print("=== MaByte DB status ===")
    print(f"DATA_DIR:        {data_dir}")
    print(f"DB_PATH:         {db_path}")
    print(f"env DATA_DIR:    {env_data_dir}")
    print(f"Railway env:     {on_railway}")
    print(f"Data dir exists: {data_dir.is_dir()}")
    print(f"Data dir write:  {'OK' if writable else f'FAIL — {write_err}'}")

    if db_path.is_file():
        stat = db_path.stat()
        print(f"DB exists:       True")
        print(f"DB size:         {_fmt_size(stat.st_size)}")
        print(f"DB mtime:        {_fmt_mtime(stat.st_mtime)}")
        n = _user_count(db_path)
        print(f"Users in DB:     {n if n is not None else 'n/a (users table missing?)'}")
    else:
        print("DB exists:       False (empty — will be created on first app boot)")

    print()
    if not writable:
        print("[!] DATA_DIR ist NICHT beschreibbar. Accounts können nicht gespeichert werden.")
        print("    Railway → Service → Volumes: Mount Path /data anlegen.")
        return 2

    if on_railway and ephemeral:
        print("[!] Railway erkannt, aber DATA_DIR liegt NICHT auf /data.")
        print("    → Jeder Redeploy löscht die DB. Volume mit Mount /data anlegen und")
        print("      DATA_DIR=/data im Service als Variable setzen.")
        print("    Details: docs/ACCOUNTS_DB.md")
        return 1

    if on_railway:
        print("[OK] Railway + /data — Accounts sollten Redeploys überleben.")
    else:
        print("[OK] Lokale Umgebung — persistent solange dieses Verzeichnis bleibt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
