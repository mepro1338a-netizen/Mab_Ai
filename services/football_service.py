"""Football live-data client — football-data.org v4 (free tier)."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from config import (
    DATA_DIR,
    FOOTBALL_FEATURES,
    FOOTBALL_DATA_CACHE_TTL,
    FOOTBALL_DATA_COMPETITION_CODES,
    FOOTBALL_DATA_LIVE_CACHE_TTL,
    FOOTBALL_DATA_STANDINGS_CACHE_TTL,
    FOOTBALL_PLAN_ORDER,
    FOOTBALL_PLANS,
    SPORTMONKS_LEAGUE_IDS,
    football_daily_ai_limit,
    football_daily_api_limit,
    football_feature_meta,
    football_has_feature,
    football_plan_rank,
    football_priority_cache,
    get_football_plan,
)
import os

from core.config import get_football_api_provider
from services.football_data_client import (
    FootballDataError,
    fd_get,
    is_fd_configured,
    map_fd_match,
    map_fd_matches,
    map_fd_standings,
)
from services.sportmonks_client import (
    SportMonksError,
    is_sm_configured,
    map_sm_fixture,
    map_sm_fixtures,
    map_sm_standings,
    sm_get,
    sm_get_all,
)

from db.app import (
    get_football_plan as db_get_football_plan,
    get_football_usage_today,
    record_football_ai_analysis,
    record_football_api_call,
)
from db.users import is_owner_user
from logger import log_warning
from security import check_rate_limit

PLAN_LABELS = {key: val.get("label", key) for key, val in FOOTBALL_PLANS.items()}
PLAN_LABELS["none"] = "Kein Football Plan"

_BERLIN_TZ = ZoneInfo("Europe/Berlin")
# Statuses that should never appear in "next matches" pools.
_FD_DONE_OR_DEAD = frozenset({"FT", "AET", "PEN", "AWD", "WO", "CANC", "PST"})
_FREE_TIER_LEAGUE_IDS = frozenset(FOOTBALL_DATA_COMPETITION_CODES.keys())
_SM_TIER_LEAGUE_IDS = frozenset(SPORTMONKS_LEAGUE_IDS.keys())
_FD_NOT_CONFIGURED = (
    "football-data.org ist auf dem Server nicht konfiguriert "
    "(FOOTBALL_DATA_API_KEY in Railway/.env). "
    "Live-Daten erscheinen sobald der Key gesetzt ist."
)
_SM_NOT_CONFIGURED = (
    "SportMonks ist auf dem Server nicht konfiguriert "
    "(SPORTMONKS_API_KEY in Railway/.env). "
    "Live-Daten erscheinen sobald der Key gesetzt ist."
)


def _provider_not_configured_msg() -> str:
    if get_football_api_provider() == "sportmonks":
        return _SM_NOT_CONFIGURED
    return _FD_NOT_CONFIGURED


def _fixture_local_date(fixture: dict[str, Any]) -> str:
    """Local (Europe/Berlin) ISO date of a fixture in API-Football shape."""
    raw = str((fixture.get("fixture") or {}).get("date") or "")
    if not raw:
        return ""
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=_BERLIN_TZ)
        return dt.astimezone(_BERLIN_TZ).date().isoformat()
    except ValueError:
        return raw[:10]


def _fixture_status_short(fixture: dict[str, Any]) -> str:
    return str(((fixture.get("fixture") or {}).get("status") or {}).get("short") or "NS")

ACTION_TO_FEATURE = {
    "match_recap": "ai_match_summary",
    "basic_prediction": "ai_predictions",
    "reel_script": "ai_reel_hooks",
    "viral_hook": "ai_reel_hooks",
    "matchday_package": "ai_match_preview",
    "optimized_package": "ai_match_preview",
    "viral_analysis": "ai_viral_analysis",
    "thumbnail_system": "ai_match_preview",
    "deep_match_analysis": "ai_elite_live_intelligence",
    "full_campaign": "ai_matchday_reports",
    "auto_posting": "automation_triggers",
}


class FootballAccessError(Exception):
    """User-facing gate for Football Premium features."""


def resolve_football_plan(username: str, session_plan: str | None = None) -> str:
    if is_owner_user(username):
        return "football_elite"
    if session_plan and session_plan in FOOTBALL_PLANS:
        return session_plan
    return db_get_football_plan(username)


def plan_label(plan_key: str) -> str:
    return PLAN_LABELS.get(plan_key, plan_key)


def feature_label(feature_id: str) -> str:
    meta = football_feature_meta(feature_id)
    return str(meta.get("label") or feature_id)


def can_access_feature(
    username: str,
    feature_id: str,
    session_plan: str | None = None,
) -> tuple[bool, str, str]:
    meta = football_feature_meta(feature_id)
    if not meta:
        return False, "Unbekanntes Feature.", "football_starter"
    plan = resolve_football_plan(username, session_plan)
    min_plan = str(meta.get("min_plan") or "football_starter")
    if is_owner_user(username) or football_has_feature(plan, feature_id):
        return True, "", plan
    need = get_football_plan(min_plan) or {}
    return (
        False,
        f"**{feature_label(feature_id)}** erfordert mindestens **{need.get('label', min_plan)}**. "
        f"Dein Plan: **{plan_label(plan)}**.",
        min_plan,
    )


def assert_feature(username: str, feature_id: str, session_plan: str | None = None) -> str:
    ok, msg, _ = can_access_feature(username, feature_id, session_plan)
    if not ok:
        raise FootballAccessError(msg)
    return resolve_football_plan(username, session_plan)


def preflight_api_request(
    username: str,
    feature_id: str,
    session_plan: str | None = None,
    *,
    api_configured: bool = True,
) -> str:
    plan = assert_feature(username, feature_id, session_plan)
    if not api_configured:
        raise FootballAccessError(_provider_not_configured_msg())
    if plan == "none" and not is_owner_user(username):
        raise FootballAccessError("Kein Football Premium Plan aktiv.")
    daily_limit = int(football_daily_api_limit(plan) or 0)
    if daily_limit <= 0 and not is_owner_user(username):
        raise FootballAccessError("Dein Plan enthält keine API-Requests.")
    used = get_football_usage_today(username)["api_calls"]
    if used >= daily_limit and not is_owner_user(username):
        raise FootballAccessError(
            f"Tageslimit API erreicht ({used:,}/{daily_limit:,}). "
            "Morgen Reset oder Upgrade auf Football Elite.".replace(",", ".")
        )
    return plan


def record_api_success(username: str, session_plan: str | None = None) -> dict:
    plan = resolve_football_plan(username, session_plan)
    total = record_football_api_call(username)
    limit = int(football_daily_api_limit(plan) or 0)
    return {"used": total, "limit": limit, "plan": plan}


def _action_feature(action: str) -> str:
    return ACTION_TO_FEATURE.get(action, "ai_match_summary")


def can_run_action(
    username: str,
    action: str,
    session_plan: str | None = None,
) -> tuple[bool, str]:
    feature_id = _action_feature(action)
    ok, msg, _ = can_access_feature(username, feature_id, session_plan)
    if not ok:
        return False, msg
    plan = resolve_football_plan(username, session_plan)
    if plan == "none" and not is_owner_user(username):
        return False, "Kein Football Premium Plan. Upgrade unter Premium."
    daily_limit = int(football_daily_ai_limit(plan) or 0)
    used = get_football_usage_today(username)["ai_analyses"]
    if used >= daily_limit and not is_owner_user(username):
        return False, (
            f"Tageslimit AI-Analysen erreicht ({used}/{daily_limit}). "
            f"Upgrade für mehr Kapazität."
        )
    return True, ""


def consume_action(
    username: str,
    action: str,
    session_plan: str | None = None,
) -> int:
    ok, msg = can_run_action(username, action, session_plan)
    if not ok:
        raise FootballAccessError(msg)
    if is_owner_user(username):
        return 1
    return record_football_ai_analysis(username)


def can_export_reels(username: str, session_plan: str | None = None) -> tuple[bool, str]:
    return can_access_feature(username, "export_reels_studio", session_plan)[:2]


def feature_matrix(plan_key: str) -> list[dict]:
    rank = football_plan_rank(plan_key)
    rows = []
    for fid, meta in FOOTBALL_FEATURES.items():
        min_rank = football_plan_rank(meta.get("min_plan", "football_starter"))
        rows.append({
            "id": fid,
            "label": meta.get("label", fid),
            "category": meta.get("category", "api"),
            "description": meta.get("description", ""),
            "min_plan": meta.get("min_plan"),
            "available": rank >= min_rank,
        })
    return rows


def usage_summary(username: str, session_plan: str | None = None) -> dict:
    plan = resolve_football_plan(username, session_plan)
    cfg = get_football_plan(plan) or {}
    usage = get_football_usage_today(username)
    api_daily = int(football_daily_api_limit(plan) or 0)
    ai_daily = int(football_daily_ai_limit(plan) or 0)
    owner = is_owner_user(username)
    return {
        "plan": plan,
        "plan_label": plan_label(plan),
        "badge": cfg.get("badge", ""),
        "live_api": bool(cfg.get("live_api_access")) or owner,
        "priority_cache": football_priority_cache(plan) or owner,
        "api_used": usage["api_calls"],
        "api_limit": api_daily,
        "ai_used": usage["ai_analyses"],
        "ai_limit": ai_daily if ai_daily < 9000 else "Unbegrenzt",
        "actions_used": usage["ai_analyses"],
        "actions_limit": ai_daily,
        "tier": FOOTBALL_PLAN_ORDER.get(plan, 0),
        "features": {
            fid: football_has_feature(plan, fid) or owner
            for fid in FOOTBALL_FEATURES
        },
    }


def tier_features(plan_key: str) -> list[str]:
    plan = get_football_plan(plan_key)
    if not plan:
        return []
    return list(plan.get("highlights") or [])


class FootballAPIError(Exception):
  """Raised when the football data provider returns an error."""

  def __init__(
      self,
      message: str,
      status_code: int | None = None,
      api_errors: list | dict | None = None,
  ):
      super().__init__(message)
      self.status_code = status_code
      self.api_errors = api_errors or []


def _filter_free_tier_fixtures(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    allowed = _SM_TIER_LEAGUE_IDS if get_football_api_provider() == "sportmonks" else _FREE_TIER_LEAGUE_IDS
    out: list[dict[str, Any]] = []
    for fx in fixtures or []:
        try:
            lid = int((fx.get("league") or {}).get("id") or 0)
        except (TypeError, ValueError):
            continue
        if lid in allowed:
            out.append(fx)
    return out


class FootballService:
  """Football data client (football-data.org or SportMonks) with memory + disk cache."""

  def __init__(self) -> None:
      self.cache_dir = Path(DATA_DIR) / "cache" / "football"
      self.cache_dir.mkdir(parents=True, exist_ok=True)
      self._memory_cache: dict[str, tuple[float, Any]] = {}
      self._last_http_debug: dict[str, Any] = {}
      self._premium_load_report: dict[str, Any] = {}

  def _use_sportmonks(self) -> bool:
      return get_football_api_provider() == "sportmonks"

  def _provider_label(self) -> str:
      return "sportmonks" if self._use_sportmonks() else "football-data.org"

  def last_http_debug(self) -> dict[str, Any]:
      return dict(self._last_http_debug)

  def _dev_mode(self) -> bool:
      return os.getenv("DEV_MODE", "").strip().lower() in ("1", "true", "yes", "on")

  def _log_http_debug(
      self,
      *,
      endpoint: str,
      params: dict[str, Any],
      status_code: int | None,
      response_length: int,
      cached: bool,
      error: str = "",
      rate_limit_remaining: str | None = None,
      headers: dict[str, str] | None = None,
      response_snippet: str = "",
      limiter: str = "",
  ) -> None:
      if not self._dev_mode():
          return
      self._last_http_debug = {
          "endpoint": endpoint,
          "params": params,
          "status_code": status_code,
          "response_length": response_length,
          "cached": cached,
          "error": error,
          "rate_limit_remaining": rate_limit_remaining,
          "headers": dict(headers or {}),
          "response_snippet": str(response_snippet or "")[:1200],
          "limiter": limiter,
      }

  def is_configured(self) -> bool:
      """True when the active provider has an API key."""
      if self._use_sportmonks():
          return is_sm_configured()
      return self.fd_enabled()

  def fd_enabled(self) -> bool:
      return is_fd_configured()

  def sm_enabled(self) -> bool:
      return is_sm_configured()

  def premium_api_enabled(self) -> bool:
      """Odds/predictions/injuries/h2h via api-sports.io — permanently disabled."""
      return False

  def _require_fd(self) -> None:
      if not self.is_configured():
          raise FootballAPIError(_provider_not_configured_msg())

  def _cache_key(self, endpoint: str, params: dict[str, Any]) -> str:
      payload = json.dumps(
          {"endpoint": endpoint, "params": params},
          sort_keys=True,
          default=str,
      )
      return hashlib.sha256(payload.encode("utf-8")).hexdigest()

  def _read_cache_any_age(self, key: str) -> Any | None:
      now = time.time()
      memory_hit = self._memory_cache.get(key)
      if memory_hit:
          return memory_hit[1]
      cache_file = self.cache_dir / f"{key}.json"
      if not cache_file.exists():
          return None
      try:
          payload = json.loads(cache_file.read_text(encoding="utf-8"))
          data = payload.get("data")
          self._memory_cache[key] = (now, data)
          return data
      except (OSError, json.JSONDecodeError, TypeError, ValueError):
          return None

  def _read_cache(self, key: str, ttl: int) -> Any | None:
      now = time.time()
      memory_hit = self._memory_cache.get(key)
      if memory_hit and now - memory_hit[0] < ttl:
          return memory_hit[1]

      cache_file = self.cache_dir / f"{key}.json"
      if not cache_file.exists():
          return None

      try:
          payload = json.loads(cache_file.read_text(encoding="utf-8"))
          if now - float(payload.get("ts", 0)) >= ttl:
              return None
          data = payload.get("data")
          self._memory_cache[key] = (now, data)
          return data
      except (OSError, json.JSONDecodeError, TypeError, ValueError):
          return None

  def _write_cache(self, key: str, data: Any) -> None:
      now = time.time()
      self._memory_cache[key] = (now, data)
      cache_file = self.cache_dir / f"{key}.json"
      try:
          cache_file.write_text(
              json.dumps({"ts": now, "data": data}, ensure_ascii=False),
              encoding="utf-8",
          )
      except OSError as exc:
          log_warning(f"Football cache write failed: {exc}")

  # ------------------------------------------------------------------
  # football-data.org v4 layer (primary fixture/standings source)
  # ------------------------------------------------------------------

  def _fd_request(
      self,
      path: str,
      params: dict[str, Any] | None = None,
      *,
      ttl: int,
      feature: str = "api_fixtures",
      username: str = "",
  ) -> dict[str, Any]:
      """Cached GET against football-data.org; serves stale cache on 429/errors."""
      if username:
          try:
              preflight_api_request(username, feature, api_configured=True)
          except FootballAccessError as exc:
              raise FootballAPIError(str(exc)) from exc

      clean_params = {k: v for k, v in (params or {}).items() if v not in (None, "")}
      cache_key = self._cache_key(f"fd:{path}", clean_params)
      cached = self._read_cache(cache_key, int(ttl))
      if cached is not None:
          self._log_http_debug(
              endpoint=f"fd:{path}",
              params=clean_params,
              status_code=200,
              response_length=len(cached.get("matches") or []) if isinstance(cached, dict) else 0,
              cached=True,
              limiter="cache",
          )
          return cached

      allowed, rate_msg = check_rate_limit(f"football_fd:{username or 'global'}")
      if not allowed:
          stale = self._read_cache_any_age(cache_key)
          if stale is not None:
              log_warning(f"football-data internal rate limit — stale cache: {path}")
              return stale
          raise FootballAPIError(rate_msg)

      try:
          payload = fd_get(path, clean_params)
      except FootballDataError as exc:
          stale = self._read_cache_any_age(cache_key)
          if stale is not None:
              log_warning(f"football-data error — serving stale cache: {path} ({exc})")
              return stale
          self._log_http_debug(
              endpoint=f"fd:{path}",
              params=clean_params,
              status_code=exc.status_code,
              response_length=0,
              cached=False,
              error=str(exc),
              limiter="api",
          )
          raise FootballAPIError(str(exc), status_code=exc.status_code) from exc

      self._write_cache(cache_key, payload)
      if username:
          try:
              record_api_success(username)
          except FootballAccessError as exc:
              raise FootballAPIError(str(exc)) from exc
      self._log_http_debug(
          endpoint=f"fd:{path}",
          params=clean_params,
          status_code=200,
          response_length=len(payload.get("matches") or []) if isinstance(payload, dict) else 0,
          cached=False,
          limiter="api",
      )
      return payload

  def _sm_request(
      self,
      path: str,
      params: dict[str, Any] | None = None,
      *,
      ttl: int,
      feature: str = "api_fixtures",
      username: str = "",
      paginate: bool = False,
  ) -> Any:
      """Cached GET against SportMonks; serves stale cache on 429/errors."""
      if username:
          try:
              preflight_api_request(username, feature, api_configured=True)
          except FootballAccessError as exc:
              raise FootballAPIError(str(exc)) from exc

      clean_params = {k: v for k, v in (params or {}).items() if v not in (None, "")}
      cache_key = self._cache_key(f"sm:{path}", {**clean_params, "paginate": paginate})
      cached = self._read_cache(cache_key, int(ttl))
      if cached is not None:
          self._log_http_debug(
              endpoint=f"sm:{path}",
              params=clean_params,
              status_code=200,
              response_length=len(cached) if isinstance(cached, list) else 1,
              cached=True,
              limiter="cache",
          )
          return cached

      allowed, rate_msg = check_rate_limit(f"football_sm:{username or 'global'}")
      if not allowed:
          stale = self._read_cache_any_age(cache_key)
          if stale is not None:
              log_warning(f"sportmonks internal rate limit — stale cache: {path}")
              return stale
          raise FootballAPIError(rate_msg)

      try:
          payload = sm_get_all(path, clean_params) if paginate else sm_get(path, clean_params)
      except SportMonksError as exc:
          stale = self._read_cache_any_age(cache_key)
          if stale is not None:
              log_warning(f"sportmonks error — serving stale cache: {path} ({exc})")
              return stale
          self._log_http_debug(
              endpoint=f"sm:{path}",
              params=clean_params,
              status_code=exc.status_code,
              response_length=0,
              cached=False,
              error=str(exc),
              limiter="api",
          )
          raise FootballAPIError(str(exc), status_code=exc.status_code) from exc

      self._write_cache(cache_key, payload)
      if username:
          try:
              record_api_success(username)
          except FootballAccessError as exc:
              raise FootballAPIError(str(exc)) from exc
      self._log_http_debug(
          endpoint=f"sm:{path}",
          params=clean_params,
          status_code=200,
          response_length=len(payload) if isinstance(payload, list) else 1,
          cached=False,
          limiter="api",
      )
      return payload

  def _fd_code(self, league_id: int) -> str | None:
      try:
          return FOOTBALL_DATA_COMPETITION_CODES.get(int(league_id))
      except (TypeError, ValueError):
          return None

  def _fd_competition_season_fixtures(
      self,
      league_id: int,
      *,
      username: str = "",
  ) -> list[dict[str, Any]]:
      """ONE call per competition (current season, 6h cache) — rate-limit friendly.

      Today/tomorrow/next/range views are filtered client-side from this pool.
      """
      code = self._fd_code(league_id)
      if not code:
          return []
      payload = self._fd_request(
          f"competitions/{code}/matches",
          {},
          ttl=int(FOOTBALL_DATA_CACHE_TTL),
          feature="api_fixtures",
          username=username,
      )
      return map_fd_matches(payload)

  def _sm_league_id(self, league_id: int) -> int | None:
      try:
          return SPORTMONKS_LEAGUE_IDS.get(int(league_id))
      except (TypeError, ValueError):
          return None

  def _sm_current_season_id(self, sm_league_id: int, *, username: str = "") -> int | None:
      payload = self._sm_request(
          f"leagues/{int(sm_league_id)}",
          {"include": "currentSeason"},
          ttl=int(FOOTBALL_DATA_CACHE_TTL),
          feature="api_fixtures",
          username=username,
      )
      league = payload.get("data") if isinstance(payload, dict) else {}
      if not isinstance(league, dict):
          league = payload if isinstance(payload, dict) else {}
      season = league.get("currentSeason") or league.get("currentseason") or {}
      try:
          return int(season.get("id"))
      except (TypeError, ValueError):
          return None

  def _sm_competition_season_fixtures(
      self,
      league_id: int,
      *,
      username: str = "",
  ) -> list[dict[str, Any]]:
      sm_lid = self._sm_league_id(league_id)
      if not sm_lid:
          return []
      season_id = self._sm_current_season_id(sm_lid, username=username)
      if not season_id:
          rows = self._sm_request(
              "fixtures",
              {"filters": f"fixtureLeagues:{sm_lid}"},
              ttl=int(FOOTBALL_DATA_CACHE_TTL),
              feature="api_fixtures",
              username=username,
              paginate=True,
          )
          return map_sm_fixtures(rows if isinstance(rows, list) else [])
      rows = self._sm_request(
          f"fixtures/seasons/{season_id}",
          {},
          ttl=int(FOOTBALL_DATA_CACHE_TTL),
          feature="api_fixtures",
          username=username,
          paginate=True,
      )
      return map_sm_fixtures(rows if isinstance(rows, list) else [])

  def _sm_fixtures_in_range(
      self,
      league_id: int,
      date_from: str,
      date_to: str,
      *,
      username: str = "",
  ) -> list[dict[str, Any]]:
      lo, hi = str(date_from)[:10], str(date_to)[:10]
      rows = self._sm_competition_season_fixtures(league_id, username=username)
      return [fx for fx in rows if lo <= _fixture_local_date(fx) <= hi]

  def _sm_premium_upcoming(
      self,
      *,
      days: int = 30,
      username: str = "",
  ) -> list[dict[str, Any]]:
      from config import FOOTBALL_TOPSPIELE_LEAGUE_IDS
      from services.football_loaders import sort_fixtures_by_priority

      today = datetime.now(_BERLIN_TZ).date()
      horizon = (today + timedelta(days=max(1, int(days)))).isoformat()
      today_s = today.isoformat()
      mapped_ids = sorted(
          int(lid) for lid in FOOTBALL_TOPSPIELE_LEAGUE_IDS if self._sm_league_id(int(lid))
      )

      composite_key = self._cache_key(
          "sm_premium_upcoming_v1", {"days": int(days), "ids": mapped_ids}
      )
      cached = self._read_cache(composite_key, 21_600)
      if isinstance(cached, list) and cached:
          return cached

      rows: list[dict[str, Any]] = []
      report: dict[str, Any] = {
          "provider": "sportmonks",
          "horizon_days": int(days),
          "leagues": {},
      }
      for lid in mapped_ids:
          try:
              part = self._sm_competition_season_fixtures(lid, username=username)
          except FootballAPIError:
              part = []
          in_window = [
              fx for fx in part
              if today_s <= _fixture_local_date(fx) <= horizon
              and _fixture_status_short(fx) not in _FD_DONE_OR_DEAD
          ]
          report["leagues"][str(lid)] = {"count": len(in_window)}
          rows.extend(in_window)
      report["total_upcoming"] = len(rows)
      self._premium_load_report = report

      seen: set[int] = set()
      deduped: list[dict[str, Any]] = []
      for fx in rows:
          fid = (fx.get("fixture") or {}).get("id")
          try:
              key = int(fid)
          except (TypeError, ValueError):
              continue
          if key in seen:
              continue
          seen.add(key)
          deduped.append(fx)

      out = sort_fixtures_by_priority(deduped)
      if out:
          self._write_cache(composite_key, out)
      return out

  def _fd_fixtures_in_range(
      self,
      league_id: int,
      date_from: str,
      date_to: str,
      *,
      username: str = "",
  ) -> list[dict[str, Any]]:
      lo, hi = str(date_from)[:10], str(date_to)[:10]
      rows = self._fd_competition_season_fixtures(league_id, username=username)
      return [fx for fx in rows if lo <= _fixture_local_date(fx) <= hi]

  def _fd_premium_upcoming(
      self,
      *,
      days: int = 30,
      username: str = "",
  ) -> list[dict[str, Any]]:
      from config import FOOTBALL_TOPSPIELE_LEAGUE_IDS
      from services.football_loaders import sort_fixtures_by_priority

      today = datetime.now(_BERLIN_TZ).date()
      horizon = (today + timedelta(days=max(1, int(days)))).isoformat()
      today_s = today.isoformat()
      mapped_ids = sorted(
          int(lid) for lid in FOOTBALL_TOPSPIELE_LEAGUE_IDS if self._fd_code(int(lid))
      )

      composite_key = self._cache_key(
          "fd_premium_upcoming_v1", {"days": int(days), "ids": mapped_ids}
      )
      cached = self._read_cache(composite_key, 21_600)
      if isinstance(cached, list) and cached:
          return cached

      rows: list[dict[str, Any]] = []
      report: dict[str, Any] = {
          "provider": "football-data.org",
          "horizon_days": int(days),
          "leagues": {},
      }
      for lid in mapped_ids:
          try:
              part = self._fd_competition_season_fixtures(lid, username=username)
          except FootballAPIError:
              part = []
          in_window = [
              fx for fx in part
              if today_s <= _fixture_local_date(fx) <= horizon
              and _fixture_status_short(fx) not in _FD_DONE_OR_DEAD
          ]
          report["leagues"][str(lid)] = {"count": len(in_window)}
          rows.extend(in_window)
      report["total_upcoming"] = len(rows)
      self._premium_load_report = report

      seen: set[int] = set()
      deduped: list[dict[str, Any]] = []
      for fx in rows:
          fid = (fx.get("fixture") or {}).get("id")
          try:
              key = int(fid)
          except (TypeError, ValueError):
              continue
          if key in seen:
              continue
          seen.add(key)
          deduped.append(fx)

      out = sort_fixtures_by_priority(deduped)
      if out:
          self._write_cache(composite_key, out)
      return out

  # ------------------------------------------------------------------
  # Public fixture/standings API (routes to football-data.org when set)
  # ------------------------------------------------------------------

  def get_recent_fixtures(
      self,
      team_id: int,
      *,
      last_count: int = 5,
      username: str = "",
  ) -> list[dict[str, Any]]:
      count = max(1, min(int(last_count), 15))
      self._require_fd()
      if self._use_sportmonks():
          end = datetime.now(_BERLIN_TZ).date()
          start = end - timedelta(days=400)
          rows = self._sm_request(
              f"fixtures/between/{start.isoformat()}/{end.isoformat()}",
              {"filters": f"participantIds:{int(team_id)}"},
              ttl=int(FOOTBALL_DATA_CACHE_TTL),
              feature="api_results",
              username=username,
              paginate=True,
          )
          mapped = [
              fx for fx in map_sm_fixtures(rows if isinstance(rows, list) else [])
              if _fixture_status_short(fx) == "FT"
          ]
          mapped.sort(
              key=lambda fx: str((fx.get("fixture") or {}).get("date") or ""),
              reverse=True,
          )
          return mapped[:count]
      payload = self._fd_request(
          f"teams/{int(team_id)}/matches",
          {"status": "FINISHED"},
          ttl=int(FOOTBALL_DATA_CACHE_TTL),
          feature="api_results",
          username=username,
      )
      rows = map_fd_matches(payload)
      rows.sort(
          key=lambda fx: str((fx.get("fixture") or {}).get("date") or ""),
          reverse=True,
      )
      return rows[:count]

  def get_fixtures_by_league_season(
      self,
      league_id: int,
      *,
      season: int | None = None,
      username: str = "",
      ttl_override: int | None = None,
  ) -> list[dict[str, Any]]:
      """All fixtures for league+season (client-side date filter for upcoming)."""
      _ = season, ttl_override
      self._require_fd()
      if self._use_sportmonks():
          return self._sm_competition_season_fixtures(int(league_id), username=username)
      return self._fd_competition_season_fixtures(int(league_id), username=username)

  def get_premium_fixtures_upcoming(
      self,
      *,
      days: int = 30,
      username: str = "",
  ) -> list[dict[str, Any]]:
      """Curated competitions — today through the next `days` days."""
      self._require_fd()
      if self._use_sportmonks():
          return self._sm_premium_upcoming(days=days, username=username)
      return self._fd_premium_upcoming(days=days, username=username)

  def get_fixtures_by_league_range(
      self,
      league_id: int,
      *,
      season: int | None = None,
      date_from: str,
      date_to: str,
      username: str = "",
      ttl_override: int | None = None,
  ) -> list[dict[str, Any]]:
      _ = season, ttl_override
      self._require_fd()
      if self._use_sportmonks():
          return self._sm_fixtures_in_range(
              int(league_id), date_from, date_to, username=username
          )
      return self._fd_fixtures_in_range(
          int(league_id), date_from, date_to, username=username
      )

  def get_fixtures_by_league_next(
      self,
      league_id: int,
      *,
      next_count: int = 30,
      username: str = "",
      ttl_override: int | None = None,
  ) -> list[dict[str, Any]]:
      _ = ttl_override
      count = max(1, min(int(next_count), 50))
      self._require_fd()
      today_s = datetime.now(_BERLIN_TZ).date().isoformat()
      if self._use_sportmonks():
          rows = self._sm_competition_season_fixtures(int(league_id), username=username)
      else:
          rows = self._fd_competition_season_fixtures(int(league_id), username=username)
      upcoming = [
          fx for fx in rows
          if _fixture_local_date(fx) >= today_s
          and _fixture_status_short(fx) not in _FD_DONE_OR_DEAD
      ]
      upcoming.sort(key=lambda fx: str((fx.get("fixture") or {}).get("date") or ""))
      return upcoming[:count]

  def get_live_fixtures(
      self,
      *,
      username: str = "",
      premium_only: bool = False,
  ) -> list[dict[str, Any]]:
      self._require_fd()
      if self._use_sportmonks():
          payload = self._sm_request(
              "livescores/inplay",
              {},
              ttl=int(FOOTBALL_DATA_LIVE_CACHE_TTL),
              feature="api_live_scores",
              username=username,
          )
          data = payload.get("data") if isinstance(payload, dict) else payload
          if isinstance(data, dict):
              data = [data]
          rows = _filter_free_tier_fixtures(map_sm_fixtures(data if isinstance(data, list) else []))
      else:
          payload = self._fd_request(
              "matches",
              {"status": "LIVE"},
              ttl=int(FOOTBALL_DATA_LIVE_CACHE_TTL),
              feature="api_live_scores",
              username=username,
          )
          rows = _filter_free_tier_fixtures(map_fd_matches(payload))
      if premium_only:
          from services.football_loaders import filter_premium_fixtures
          return filter_premium_fixtures(rows)
      return rows

  def get_fixtures_by_date(
      self,
      date: str,
      *,
      league_id: int | None = None,
      season: int | None = None,
      username: str = "",
      ttl_override: int | None = None,
  ) -> list[dict[str, Any]]:
      """Fixtures for YYYY-MM-DD, optional league filter."""
      _ = season, ttl_override
      day = str(date).strip()[:10]
      self._require_fd()
      if league_id:
          if self._use_sportmonks():
              return self._sm_fixtures_in_range(int(league_id), day, day, username=username)
          return self._fd_fixtures_in_range(int(league_id), day, day, username=username)
      today_s = datetime.now(_BERLIN_TZ).date().isoformat()
      ttl = 1_800 if day == today_s else int(FOOTBALL_DATA_CACHE_TTL)
      if self._use_sportmonks():
          rows = self._sm_request(
              f"fixtures/date/{day}",
              {},
              ttl=ttl,
              feature="api_fixtures",
              username=username,
              paginate=True,
          )
          return _filter_free_tier_fixtures(map_sm_fixtures(rows if isinstance(rows, list) else []))
      try:
          day_after = (datetime.fromisoformat(day) + timedelta(days=1)).date().isoformat()
      except ValueError:
          day_after = day
      payload = self._fd_request(
          "matches",
          {"dateFrom": day, "dateTo": day_after},
          ttl=ttl,
          feature="api_fixtures",
          username=username,
      )
      return _filter_free_tier_fixtures(map_fd_matches(payload))

  def get_fixture(self, fixture_id: int, *, username: str = "") -> dict[str, Any] | None:
      self._require_fd()
      if self._use_sportmonks():
          payload = self._sm_request(
              f"fixtures/{int(fixture_id)}",
              {},
              ttl=300,
              feature="api_fixtures",
              username=username,
          )
          match = payload.get("data") if isinstance(payload, dict) else None
          if not isinstance(match, dict) or not match.get("id"):
              return None
          return map_sm_fixture(match)
      payload = self._fd_request(
          f"matches/{int(fixture_id)}",
          {},
          ttl=300,
          feature="api_fixtures",
          username=username,
      )
      match = payload.get("match") if isinstance(payload.get("match"), dict) else payload
      if not isinstance(match, dict) or not match.get("id"):
          return None
      return map_fd_match(match)

  def get_head_to_head(
      self,
      team1_id: int,
      team2_id: int,
      *,
      last_count: int = 5,
      username: str = "",
  ) -> list[dict[str, Any]]:
      _ = team1_id, team2_id, last_count, username
      return []

  def get_standings(
      self,
      league_id: int,
      *,
      season: int | None = None,
      username: str = "",
  ) -> list[dict[str, Any]]:
      _ = season
      self._require_fd()
      if self._use_sportmonks():
          sm_lid = self._sm_league_id(int(league_id))
          if not sm_lid:
              return []
          season_id = self._sm_current_season_id(sm_lid, username=username)
          if not season_id:
              return []
          payload = self._sm_request(
              f"standings/seasons/{season_id}",
              {"include": "participant;details"},
              ttl=int(FOOTBALL_DATA_STANDINGS_CACHE_TTL),
              feature="api_standings",
              username=username,
          )
          rows = payload.get("data") if isinstance(payload, dict) else []
          if not isinstance(rows, list):
              rows = [rows] if isinstance(rows, dict) else []
          participants: dict[int, dict[str, Any]] = {}
          for row in rows:
              part = row.get("participant") if isinstance(row, dict) else None
              if isinstance(part, dict) and part.get("id") is not None:
                  participants[int(part["id"])] = part
          league_payload = self._sm_request(
              f"leagues/{sm_lid}",
              {"include": "country"},
              ttl=int(FOOTBALL_DATA_STANDINGS_CACHE_TTL),
              feature="api_standings",
              username=username,
          )
          league_meta = league_payload.get("data") if isinstance(league_payload, dict) else {}
          return map_sm_standings(
              rows,
              int(league_id),
              league_meta=league_meta if isinstance(league_meta, dict) else {},
              participants=participants,
          )
      code = self._fd_code(int(league_id))
      if not code:
          return []
      payload = self._fd_request(
          f"competitions/{code}/standings",
          {},
          ttl=int(FOOTBALL_DATA_STANDINGS_CACHE_TTL),
          feature="api_standings",
          username=username,
      )
      return map_fd_standings(payload, int(league_id))

  def get_fixture_predictions(
      self,
      fixture_id: int,
      *,
      username: str = "",
  ) -> list[dict[str, Any]]:
      _ = fixture_id, username
      return []

  def get_fixture_odds(
      self,
      fixture_id: int,
      *,
      username: str = "",
  ) -> list[dict[str, Any]]:
      _ = fixture_id, username
      return []

  def get_odds_for_fixture(
      self,
      fixture_id: int,
      *,
      username: str = "",
  ) -> dict[str, float | None]:
      """Convenience: 1X2 decimal odds for a fixture."""
      from services.football_board import get_odds_for_fixture as _get

      return _get(self, int(fixture_id), username=username)

  def get_team_injuries(
      self,
      team_id: int,
      *,
      season: int | None = None,
      username: str = "",
  ) -> list[dict[str, Any]]:
      _ = team_id, season, username
      return []


def fixture_label(fixture: dict[str, Any]) -> str:
  """Human-readable one-line label for select boxes."""
  teams = fixture.get("teams") or {}
  goals = fixture.get("goals") or {}
  meta = fixture.get("fixture") or {}
  home = (teams.get("home") or {}).get("name") or "Home"
  away = (teams.get("away") or {}).get("name") or "Away"
  date = str(meta.get("date") or "")[:10]
  status = ((meta.get("status") or {}).get("short") or "NS")
  home_goals = goals.get("home")
  away_goals = goals.get("away")
  if home_goals is not None and away_goals is not None:
      score = f"{home_goals}-{away_goals}"
  else:
      score = status
  league = ((fixture.get("league") or {}).get("name") or "").strip()
  prefix = f"{league} | " if league else ""
  return f"{prefix}{date} | {home} vs {away} ({score})"


def fixture_team_names(fixture: dict[str, Any]) -> tuple[str, str]:
  teams = fixture.get("teams") or {}
  home = (teams.get("home") or {}).get("name") or ""
  away = (teams.get("away") or {}).get("name") or ""
  return home, away


_service: FootballService | None = None


def get_football_service() -> FootballService:
  global _service
  if _service is None:
      _service = FootballService()
  return _service
