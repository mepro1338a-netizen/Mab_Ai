"""Video automation — grand/elite + automation_unlocked only."""
from __future__ import annotations

from db.video_engine import create_scheduled_post, list_scheduled_posts, update_scheduled_post
from services.video_engine import can_use_automation, run_video_job


def create_automation_rule(
    username: str,
    *,
    plan: str,
    automation_unlocked: bool,
    platform: str,
    scheduled_at: str,
    frequency: str,
    prompt_template: str,
    hashtag_set: str,
    auto_caption: bool,
    auto_post: bool,
    user_consent: bool,
) -> tuple[dict | None, str | None]:
    if not can_use_automation(plan, automation_unlocked):
        return None, "Automation ab Grand-Plan + Unlock."
    if auto_post and not user_consent:
        return None, "Auto-Post erfordert ausdrückliche Zustimmung."
    post = create_scheduled_post(
        username,
        platform=platform,
        scheduled_at=scheduled_at,
        frequency=frequency,
        prompt_template=prompt_template,
        hashtag_set=hashtag_set,
        auto_caption=auto_caption,
        auto_post=auto_post,
        user_consent=user_consent,
    )
    return post, None


def process_due_posts(
    username: str,
    *,
    plan: str,
    automation_unlocked: bool,
    dry_run: bool = True,
) -> list[str]:
    """Process scheduled posts that are due — safe dry_run default."""
    if not can_use_automation(plan, automation_unlocked):
        return []
    logs: list[str] = []
    for post in list_scheduled_posts(username):
        if post.get("status") not in ("planned", "creating"):
            continue
        post_id = post["id"]
        update_scheduled_post(post_id, status="creating")
        if dry_run or not post.get("auto_post"):
            update_scheduled_post(post_id, status="ready_to_publish")
            logs.append(f"{post_id}: ready_to_publish (manueller Export)")
            continue
        # Real auto-post only when OAuth connected — handled in social_publish
        update_scheduled_post(post_id, status="ready_to_publish")
        logs.append(f"{post_id}: wartet auf OAuth-Verbindung")
    return logs
