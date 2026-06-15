#!/usr/bin/env python3
"""
MaByte SQLite migration helper — inspect, backup, restore mabai.db.

Default path: {DATA_DIR}/mabai.db (see config.py). Override with --db PATH.

Examples:
  python tools/db_migrate.py inspect
  python tools/db_migrate.py backup --out data/backups/mabai-20260615.db
  python tools/db_migrate.py export-sql --out data/backups/mabai-20260615.sql
  python tools/db_migrate.py verify --db data/backups/mabai-20260615.db
  python tools/db_migrate.py restore --from data/backups/mabai-20260615.db --force
"""
from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def default_data_dir() -> Path:
    env = os.environ.get("DATA_DIR", "").strip()
    if env:
        return Path(env)
    if os.environ.get("RAILWAY_ENVIRONMENT"):
        return Path("/data")
    return ROOT / "data"


def default_db_path() -> Path:
    return default_data_dir() / "mabai.db"


DATA_DIR = default_data_dir()
DB_PATH = default_db_path()

SYSTEM_TABLES = {"sqlite_sequence", "sqlite_stat1", "sqlite_stat4"}


def resolve_db(path: str | None) -> Path:
    return Path(path).resolve() if path else DB_PATH


def connect(db: Path) -> sqlite3.Connection:
    if not db.is_file():
        raise FileNotFoundError(f"Database not found: {db}")
    conn = sqlite3.connect(db, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def list_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    return [r["name"] for r in rows if r["name"] not in SYSTEM_TABLES]


def row_count(conn: sqlite3.Connection, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) AS n FROM [{table}]").fetchone()["n"]


def cmd_inspect(args: argparse.Namespace) -> int:
    db = resolve_db(args.db)
    data_dir = db.parent
    print(f"DATA_DIR: {data_dir}")
    print(f"DB:       {db}")
    if not db.is_file():
        print("Status:   NOT FOUND")
        return 1

    size = db.stat().st_size
    print(f"Size:     {size:,} bytes ({size / 1024:.1f} KiB)")

    conn = connect(db)
    try:
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        print(f"Integrity: {integrity}")
        if integrity != "ok":
            return 2

        tables = list_tables(conn)
        print(f"Tables:   {len(tables)}")
        total = 0
        for name in tables:
            count = row_count(conn, name)
            total += count
            print(f"  {name}: {count:,}")
        print(f"Total rows (user tables): {total:,}")

        if "users" in tables:
            users = conn.execute(
                "SELECT id, username, email, role, created_at FROM users ORDER BY id LIMIT 20"
            ).fetchall()
            if users:
                print("\nUsers (max 20):")
                for u in users:
                    print(
                        f"  id={u['id']} username={u['username']!r} "
                        f"email={u['email']!r} role={u['role']}"
                    )
            else:
                print("\nUsers: (empty)")
    finally:
        conn.close()
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    return cmd_inspect(args)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def cmd_backup(args: argparse.Namespace) -> int:
    db = resolve_db(args.db)
    if not db.is_file():
        print(f"Source DB not found: {db}", file=sys.stderr)
        return 1

    if args.out:
        dest = Path(args.out).resolve()
    else:
        dest = DATA_DIR / "backups" / f"mabai-{_timestamp()}.db"

    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not args.force:
        print(f"Refusing to overwrite {dest} (use --force)", file=sys.stderr)
        return 1

    shutil.copy2(db, dest)
    print(f"Copied {db} -> {dest} ({dest.stat().st_size:,} bytes)")
    return cmd_verify(argparse.Namespace(db=str(dest), force=False))


def cmd_export_sql(args: argparse.Namespace) -> int:
    db = resolve_db(args.db)
    if not db.is_file():
        print(f"Source DB not found: {db}", file=sys.stderr)
        return 1

    if args.out:
        dest = Path(args.out).resolve()
    else:
        dest = DATA_DIR / "backups" / f"mabai-{_timestamp()}.sql"

    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not args.force:
        print(f"Refusing to overwrite {dest} (use --force)", file=sys.stderr)
        return 1

    try:
        proc = subprocess.run(
            ["sqlite3", str(db), ".dump"],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        print(
            "sqlite3 CLI not found. Use 'backup' to copy mabai.db, "
            "or install sqlite3 and retry.",
            file=sys.stderr,
        )
        return 1
    except subprocess.CalledProcessError as exc:
        print(exc.stderr or exc.stdout, file=sys.stderr)
        return 1

    dest.write_text(proc.stdout, encoding="utf-8")
    print(f"SQL dump written: {dest} ({dest.stat().st_size:,} bytes)")
    return 0


def cmd_restore(args: argparse.Namespace) -> int:
    source = Path(args.from_path).resolve()
    if not source.is_file():
        print(f"Backup not found: {source}", file=sys.stderr)
        return 1

    target = resolve_db(args.db)
    if target.exists() and not args.force:
        print(
            f"Target exists: {target}. Use --force to replace.",
            file=sys.stderr,
        )
        return 1

    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        backup = target.with_suffix(f".before-restore-{_timestamp()}.db")
        shutil.copy2(target, backup)
        print(f"Previous DB saved: {backup}")

    shutil.copy2(source, target)
    print(f"Restored {source} -> {target}")
    return cmd_verify(argparse.Namespace(db=str(target), force=False))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="MaByte SQLite inspect / backup / restore for Railway migration.",
    )
    p.add_argument(
        "--db",
        help=f"SQLite file (default: {DB_PATH})",
    )

    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("inspect", help="Integrity check, tables, row counts")
    sub.add_parser("verify", help="Alias for inspect")

    backup = sub.add_parser("backup", help="Copy mabai.db to data/backups/")
    backup.add_argument("--out", help="Destination .db path")
    backup.add_argument("--force", action="store_true", help="Overwrite destination")

    export = sub.add_parser("export-sql", help="sqlite3 .dump to .sql file")
    export.add_argument("--out", help="Destination .sql path")
    export.add_argument("--force", action="store_true", help="Overwrite destination")

    restore = sub.add_parser("restore", help="Replace mabai.db from backup copy")
    restore.add_argument(
        "--from",
        dest="from_path",
        required=True,
        help="Source .db backup file",
    )
    restore.add_argument("--force", action="store_true", help="Replace existing DB")

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handlers = {
        "inspect": cmd_inspect,
        "verify": cmd_verify,
        "backup": cmd_backup,
        "export-sql": cmd_export_sql,
        "restore": cmd_restore,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
