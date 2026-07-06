"""MaByte database facade — backward-compatible imports for `from database import ...`."""
import os
import sqlite3
import sys
from pathlib import Path

from db.core import *  # noqa: F403
from db.users import *  # noqa: F403  # includes secure_set_football_plan, register_account
from db.support import *  # noqa: F403
from db.video_engine import *  # noqa: F403
from db.app import *  # noqa: F403

from db.app import force_owner_account  # noqa: F401

# Keep compatibility for payments module
from db.app import record_purchase  # noqa: F401
from db.app import payment_already_paid  # noqa: F401
from db.app import list_usage, recent_activity, usage_summary  # noqa: F401

# Back-compat explicit imports (some modules import from database directly)
from db.app import (  # noqa: F401
    get_football_plan,
    set_football_plan,
    get_football_usage_today,
    record_football_api_call,
    record_football_ai_actions,
    record_football_ai_analysis,
)

_db_ready = False


def _resolve_paths() -> tuple[Path, Path]:
    """Return (DATA_DIR, DB_PATH) resolved to absolute paths."""
    from config import DATA_DIR, DB_PATH

    return Path(DATA_DIR).resolve(), Path(DB_PATH).resolve()


def _write_test(data_dir: Path) -> tuple[bool, str]:
    """Touch a sentinel file in DATA_DIR to prove the volume is writable."""
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


def _looks_ephemeral(data_dir: Path) -> bool:
    """Heuristic: on Railway, only `/data` (or subpaths) survives redeploys.

    Anything else — including the fallback `<repo>/data` inside the container —
    is wiped on every deploy.
    """
    try:
        s = str(data_dir)
    except Exception:
        return False
    return not (s == "/data" or s.startswith("/data/"))


def log_db_boot_diagnostics() -> None:
    """Print DB path + volume state + user count so the user can see in Railway logs
    whether they are running on a persistent volume or an ephemeral filesystem.

    Called from `ensure_db_ready` on every cold start.
    """
    try:
        from logger import log_info, log_warning
    except Exception:
        def log_info(msg: str, **_: object) -> None:  # type: ignore[misc]
            print(f"[MaByte] INFO  {msg}", file=sys.stderr)

        def log_warning(msg: str, **_: object) -> None:  # type: ignore[misc]
            print(f"[MaByte] WARN  {msg}", file=sys.stderr)

    data_dir, db_path = _resolve_paths()
    env_data_dir = os.getenv("DATA_DIR", "").strip()
    on_railway = bool(
        os.getenv("RAILWAY_ENVIRONMENT")
        or os.getenv("RAILWAY_PROJECT_ID")
        or os.getenv("RAILWAY_SERVICE_ID")
    )

    db_exists = db_path.is_file()
    db_size = db_path.stat().st_size if db_exists else 0
    users_before = _user_count(db_path)
    writable, write_err = _write_test(data_dir)

    log_info(
        "DB boot: "
        f"DATA_DIR={data_dir} "
        f"DB_PATH={db_path} "
        f"env_DATA_DIR={env_data_dir or '(unset)'} "
        f"railway={on_railway} "
        f"db_exists={db_exists} "
        f"db_size={db_size} "
        f"users_before_init={users_before if users_before is not None else 'n/a'} "
        f"writable={writable}"
    )

    if not writable:
        log_warning(
            f"DATA_DIR nicht beschreibbar ({data_dir}): {write_err} — "
            "Accounts können NICHT gespeichert werden. Volume-Mount auf Railway prüfen."
        )
        return

    if on_railway and _looks_ephemeral(data_dir):
        log_warning(
            "Railway erkannt, aber DATA_DIR liegt NICHT auf /data "
            f"(aktuell: {data_dir}). Das Verzeichnis wird bei JEDEM Redeploy geloescht "
            "→ alle Accounts gehen verloren. In Railway → Service → Volumes ein Volume "
            "mit Mount Path /data erstellen und DATA_DIR=/data setzen. "
            "Siehe docs/ACCOUNTS_DB.md."
        )
    elif on_railway and not env_data_dir:
        log_warning(
            "Railway erkannt, aber DATA_DIR ist als ENV-Variable nicht gesetzt. "
            "Zur Sicherheit DATA_DIR=/data im Railway-Service als Variable setzen."
        )


def ensure_db_ready() -> bool:
    """Idempotent DB init — safe for Railway cold starts."""
    global _db_ready
    if _db_ready:
        return True
    try:
        log_db_boot_diagnostics()
        init_db()
        force_owner_account()
        _db_ready = True
        try:
            from logger import log_info

            _, db_path = _resolve_paths()
            users_after = _user_count(db_path)
            log_info(
                "Database initialized. "
                f"db_path={db_path} "
                f"users_after_init={users_after if users_after is not None else 'n/a'}"
            )
        except Exception:
            pass
        return True
    except Exception as exc:
        try:
            from logger import log_error
            log_error(f"ensure_db_ready failed: {exc}")
        except Exception:
            print(f"[MaByte] ensure_db_ready failed: {exc}", file=sys.stderr)
        return False
