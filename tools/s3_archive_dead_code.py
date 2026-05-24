"""Move unused modules to archive/legacy/ (no deletion)."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "archive" / "legacy"
ARCHIVE.mkdir(parents=True, exist_ok=True)

DEAD_ROOT = [
    "auth.py",
    "ui_helpers.py",
    "ui_sidebar.py",
    "ui_styles.py",
    "reedem_tracking.py",
    "backend.py",
    "ai.py",
    "ai_pipeline.py",
    "ai_service.py",
    "providers.py",
    "chat_memory.py",
    "reels_db.py",
    "reels_scheduler.py",
    "reels_service.py",
    "social_integrations.py",
    "abuse_guard.py",
    "queue_manager.py",
    "costs.py",
    "tokens.py",
    "admin_fix.py",
    "railway_admin.py",
    "db_manager.py",
    "test_db_manager.py",
    "session_manager.py",
    "coding_service.py",
    "migrations.py",
]

DEAD_PAGES = [
    "pages/coding.py",
]

moved = []
for rel in DEAD_ROOT + DEAD_PAGES:
    src = ROOT / rel
    if not src.exists():
        continue
    dest = ARCHIVE / rel.replace("/", "_")
    if dest.exists():
        continue
    shutil.move(str(src), str(dest))
    moved.append(rel)

README = ARCHIVE / "README.md"
README.write_text(
    "# Archived legacy modules\n\n"
    "Moved during S3 refactor. Not imported by the live Streamlit app.\n"
    "Restore by moving files back to project root.\n\n"
    "## Files\n\n"
    + "\n".join(f"- `{name}`" for name in moved)
    + "\n",
    encoding="utf-8",
)
print("archived:", len(moved), "files")
