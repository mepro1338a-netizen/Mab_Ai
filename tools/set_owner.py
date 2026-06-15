#!/usr/bin/env python3
"""Promote the configured owner account (role=owner, admin_level=1337).

Uses OWNER_USERNAME from env (default: mepro1337). Avoids full app imports so it
works as a Railway one-off after DB restore.

Examples:
  python tools/set_owner.py
  python tools/set_owner.py --username mepro1337
  railway run python tools/set_owner.py
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse db path resolution from db_migrate (no config.py import)
from tools.db_migrate import default_db_path  # noqa: E402

DEFAULT_OWNER = "mepro1337"
ELITE_TOKENS = 20_000


def owner_username() -> str:
    return os.getenv("OWNER_USERNAME", DEFAULT_OWNER).strip().lower()


def normalize_username(username: str) -> str:
    return (username or "").strip().lower()


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info([{table}])").fetchall()
    return {r[1] for r in rows}


def promote_owner(db: Path, username: str) -> int:
    username = normalize_username(username)
    if not db.is_file():
        print(f"Database not found: {db}")
        return 1

    conn = sqlite3.connect(db, timeout=30)
    conn.row_factory = sqlite3.Row
    cols = table_columns(conn, "users")
    select_cols = [c for c in ("username", "role", "admin_level", "plan", "football_plan") if c in cols]
    row = conn.execute(
        f"SELECT {', '.join(select_cols)} FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    if not row:
        print(f"User not found: {username!r} (DB: {db})")
        print("Register the account first, then re-run this script.")
        conn.close()
        return 1

    conn.execute(
        "UPDATE users SET role = ?, admin_level = ? WHERE username = ?",
        ("owner", 1337, username),
    )
    if "plan" in cols and row["plan"] != "elite":
        if "tokens" in cols:
            conn.execute(
                "UPDATE users SET plan = ?, tokens = ? WHERE username = ?",
                ("elite", ELITE_TOKENS, username),
            )
        else:
            conn.execute(
                "UPDATE users SET plan = ? WHERE username = ?",
                ("elite", username),
            )
    if "football_plan" in cols and (row["football_plan"] or "none") != "football_elite":
        conn.execute(
            "UPDATE users SET football_plan = ? WHERE username = ?",
            ("football_elite", username),
        )
    conn.commit()

    updated = conn.execute(
        f"SELECT {', '.join(select_cols)} FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()

    parts = [
        f"role={updated['role']}",
        f"admin_level={updated['admin_level']}",
    ]
    if "plan" in cols:
        parts.append(f"plan={updated['plan']}")
    if "football_plan" in cols:
        parts.append(f"football_plan={updated['football_plan']}")
    print(f"Owner set: {updated['username']!r} " + " ".join(parts))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Set MaByte owner account in SQLite.")
    parser.add_argument("--db", default=None, help="SQLite file (default: DATA_DIR/mabai.db)")
    parser.add_argument(
        "--username",
        default=owner_username(),
        help=f"Username to promote (default: OWNER_USERNAME={owner_username()})",
    )
    args = parser.parse_args()
    db = Path(args.db).resolve() if args.db else default_db_path()
    return promote_owner(db, args.username)


if __name__ == "__main__":
    raise SystemExit(main())
