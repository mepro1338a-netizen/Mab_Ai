"""
Elite Football Automation — matchday reports, reel pipeline, scheduled posting architecture.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import DATA_DIR, OPENAI_API_KEY, OPENAI_TEXT_MODEL


AUTOMATION_DIR = DATA_DIR / "football" / "automations"


WORKFLOW_CARDS: list[dict[str, str]] = [
    {
        "id": "matchday_report",
        "title": "Auto Matchday Report",
        "desc": "Täglicher AI-Report für gewählte Ligen — E-Mail/Export vorbereitet.",
        "min_plan": "football_elite",
    },
    {
        "id": "auto_reel",
        "title": "Auto Reel Generation",
        "desc": "Top-Spiele → Hook + Caption + Voiceover-Skript in Queue.",
        "min_plan": "football_elite",
    },
    {
        "id": "scheduled_social",
        "title": "Scheduled Social Posting",
        "desc": "TikTok / Reels / Shorts Queue mit OAuth (Architektur bereit).",
        "min_plan": "football_elite",
    },
    {
        "id": "multi_agent",
        "title": "Multi-Agent Workflow",
        "desc": "Preview Agent → Viral Agent → Publish Agent (Elite).",
        "min_plan": "football_elite",
    },
]


@dataclass
class AutomationJob:
    id: str
    workflow_id: str
    title: str
    status: str = "pending"  # pending | running | done | failed
    schedule: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    result_preview: str = ""


def _user_file(username: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in (username or "anon"))
    AUTOMATION_DIR.mkdir(parents=True, exist_ok=True)
    return AUTOMATION_DIR / f"{safe}.json"


def load_jobs(username: str) -> list[dict[str, Any]]:
    path = _user_file(username)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_jobs(username: str, jobs: list[dict[str, Any]]) -> None:
    _user_file(username).write_text(
        json.dumps(jobs[:30], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def enqueue_workflow(
    username: str,
    workflow_id: str,
    *,
    title: str,
    schedule: str = "",
    payload: dict | None = None,
) -> AutomationJob:
    job = AutomationJob(
        id=uuid.uuid4().hex[:10],
        workflow_id=workflow_id,
        title=title,
        schedule=schedule,
        payload=payload or {},
        status="pending",
    )
    jobs = load_jobs(username)
    jobs.insert(0, asdict(job))
    save_jobs(username, jobs)
    return job


def generate_matchday_report_auto(
    league_label: str,
    matches_note: str,
) -> tuple[str, str]:
    if not (OPENAI_API_KEY or "").strip():
        return (
            f"# Matchday Report · {league_label}\n\n"
            f"Spiele: {matches_note}\n\n"
            "## Highlights\n- Top 3 Storylines\n\n## Creator Picks\n- Reel 1\n- Reel 2\n",
            "fallback",
        )
    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=OPENAI_TEXT_MODEL,
            messages=[
                {"role": "system", "content": "Football matchday editor für Creator-Netzwerke."},
                {
                    "role": "user",
                    "content": f"Liga: {league_label}\nSpiele:\n{matches_note}\n\nReport mit Highlights, Upset Watch, Creator Picks.",
                },
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        return (resp.choices[0].message.content or "").strip(), "openai"
    except Exception:
        return (
            f"# Matchday Report · {league_label}\n\n{matches_note}\n\n*(Offline-Fallback)*",
            "fallback",
        )
