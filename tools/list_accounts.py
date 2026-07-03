#!/usr/bin/env python3
"""List / count all MaByte accounts (users table) — never prints passwords.

Reads the same SQLite file the app uses: {DATA_DIR}/mabai.db (see config.py).
Safe for local use and as a Railway one-off:

  python tools/list_accounts.py
  python tools/list_accounts.py --count
  python tools/list_accounts.py --csv accounts.csv
  railway run python tools/list_accounts.py
"""
from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse DB path resolution (no config.py import → works as a Railway one-off).
from tools.db_migrate import default_db_path  # noqa: E402

# Columns worth showing — password_hash / oauth_sub are intentionally excluded.
SAFE_COLUMNS = (
    "id",
    "username",
    "email",
    "role",
    "admin_level",
    "plan",
    "football_plan",
    "tokens",
    "is_banned",
    "oauth_provider",
    "created_at",
    "last_login",
)


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info([{table}])").fetchall()
    return [r[1] for r in rows]


def fetch_accounts(db: Path) -> tuple[list[str], list[sqlite3.Row]]:
    conn = sqlite3.connect(db, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        available = table_columns(conn, "users")
        if not available:
            raise RuntimeError("users table not found")
        cols = [c for c in SAFE_COLUMNS if c in available]
        rows = conn.execute(
            f"SELECT {', '.join(cols)} FROM users ORDER BY id"
        ).fetchall()
        return cols, rows
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="List or count MaByte accounts (no passwords)."
    )
    parser.add_argument("--db", default=None, help="SQLite file (default: DATA_DIR/mabai.db)")
    parser.add_argument("--count", action="store_true", help="Print only the account count")
    parser.add_argument("--csv", dest="csv_out", help="Write all accounts to a CSV file")
    args = parser.parse_args()

    db = Path(args.db).resolve() if args.db else default_db_path()
    print(f"DB: {db}")
    if not db.is_file():
        print("Status: NOT FOUND (no accounts stored at this path)")
        return 1

    try:
        cols, rows = fetch_accounts(db)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Accounts: {len(rows)}")
    if args.count:
        return 0

    if args.csv_out:
        out = Path(args.csv_out).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(cols)
            for row in rows:
                writer.writerow([row[c] for c in cols])
        print(f"CSV written: {out} ({len(rows)} rows, no passwords)")
        return 0

    if not rows:
        print("(no accounts yet)")
        return 0

    for row in rows:
        parts = [f"{c}={row[c]!r}" for c in cols]
        print("  " + " ".join(parts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
