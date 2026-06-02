"""Football live-data client for API-Football (api-sports.io)."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests

from config import (
    DATA_DIR,
    FOOTBALL_API_BASE_URL,
    FOOTBALL_API_CACHE_TTL,
    FOOTBALL_FEATURES,
    FOOTBALL_API_FIXTURES_CACHE_TTL,
    FOOTBALL_API_INJURIES_CACHE_TTL,
    FOOTBALL_API_KEY,
    FOOTBALL_API_LIVE_CACHE_TTL,
    FOOTBALL_API_STANDINGS_CACHE_TTL,
    FOOTBALL_API_TIMEOUT,
    FOOTBALL_BETTING_CORE_LEAGUE_IDS,
    FOOTBALL_DEFAULT_SEASON,
    FOOTBALL_PLAN_ORDER,
    FOOTBALL_PLANS,
    football_api_season,
    football_api_seasons_to_try,
    football_daily_ai_limit,
    football_daily_api_limit,
    football_feature_meta,
    football_has_feature,
    football_plan_rank,
    football_priority_cache,
    get_football_plan,
)
import os

from db.app import (
    get_football_plan as db_get_football_plan,
    get_football_usage_today,
    record_football_ai_analysis,
    record_football_api_call,
)
from db.users import is_owner_user
from logger import log_error, log_info, log_warning
from security import check_rate_limit

PLAN_LABELS = {key: val.get("label", key) for key, val in FOOTBALL_PLANS.items()}
PLAN_LABELS["none"] = "Kein Football Plan"

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
        raise FootballAccessError(
            "API-Football ist auf dem Server noch nicht konfiguriert "
            "(FOOTBALL_API_KEY in Railway/.env). Dein Plan bleibt aktiv — "
            "Live-Daten erscheinen sobald der Key gesetzt ist."
        )
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


class FootballService:
  """API-Football client with memory + disk cache and rate-limit handling."""

  def __init__(self) -> None:
      self.base_url = FOOTBALL_API_BASE_URL.rstrip("/")
      self.cache_dir = Path(DATA_DIR) / "cache" / "football"
      self.cache_dir.mkdir(parents=True, exist_ok=True)
      self._memory_cache: dict[str, tuple[float, Any]] = {}
      self._inflight: set[str] = set()
      self._last_http_debug: dict[str, Any] = {}

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
      return bool(FOOTBALL_API_KEY.strip())

  def _cache_key(self, endpoint: str, params: dict[str, Any]) -> str:
      payload = json.dumps(
          {"endpoint": endpoint, "params": params},
          sort_keys=True,
          default=str,
      )
      return hashlib.sha256(payload.encode("utf-8")).hexdigest()

  def _ttl_for(self, endpoint: str, live: bool, username: str = "") -> int:
      # Explicit per-endpoint TTL targets (seconds)
      # - fixtures_by_date: 10 min
      # - premium upcoming: handled via ttl_override when calling _request
      # - odds: 30 min
      # - predictions: 6 h
      # - injuries: 6 h
      # - standings: 12 h
      if endpoint == "standings":
          return max(43_200, int(FOOTBALL_API_STANDINGS_CACHE_TTL))
      if endpoint == "injuries":
          return max(21_600, int(FOOTBALL_API_INJURIES_CACHE_TTL))
      if endpoint == "predictions":
          return 21_600
      if endpoint == "odds":
          return 1_800
      if endpoint == "fixtures" and not live:
          return max(600, int(FOOTBALL_API_FIXTURES_CACHE_TTL))
      if live or endpoint in {"fixtures", "fixtures/statistics"}:
          return max(60, int(FOOTBALL_API_LIVE_CACHE_TTL))
      return max(60, int(FOOTBALL_API_CACHE_TTL))

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

  def _parse_api_errors(self, payload: dict[str, Any]) -> list | dict:
      errors = payload.get("errors") or []
      if isinstance(errors, dict):
          return errors
      if isinstance(errors, list):
          return errors
      return []

  def _request(
      self,
      endpoint: str,
      params: dict[str, Any] | None = None,
      *,
      feature: str = "api_fixtures",
      live: bool = False,
      username: str = "",
      use_cache: bool = True,
      ttl_override: int | None = None,
  ) -> list[dict[str, Any]]:
      if username:
          try:
              preflight_api_request(
                  username,
                  feature,
                  api_configured=self.is_configured(),
              )
          except FootballAccessError as exc:
              raise FootballAPIError(str(exc)) from exc

      if not self.is_configured():
          raise FootballAPIError(
              "API-Football ist auf dem Server noch nicht konfiguriert "
              "(FOOTBALL_API_KEY in Railway/.env). Dein Plan bleibt aktiv."
          )

      clean_params = {k: v for k, v in (params or {}).items() if v not in (None, "")}
      cache_key = self._cache_key(endpoint, clean_params)
      ttl = int(ttl_override) if ttl_override is not None else self._ttl_for(endpoint, live, username)

      if use_cache:
          cached = self._read_cache(cache_key, ttl)
          if cached is not None:
              self._log_http_debug(
                  endpoint=endpoint,
                  params=clean_params,
                  status_code=200,
                  response_length=len(cached) if isinstance(cached, list) else 0,
                  cached=True,
                  limiter="cache",
              )
              return cached

      if cache_key in self._inflight:
          for _ in range(80):
              time.sleep(0.05)
              if use_cache:
                  cached = self._read_cache(cache_key, ttl)
                  if cached is not None:
                      self._log_http_debug(
                          endpoint=endpoint,
                          params=clean_params,
                          status_code=200,
                          response_length=len(cached) if isinstance(cached, list) else 0,
                          cached=True,
                      )
                      return cached
              if cache_key not in self._inflight:
                  break

      self._inflight.add(cache_key)
      try:
          return self._http_request(
              endpoint,
              clean_params,
              cache_key=cache_key,
              ttl=ttl,
              feature=feature,
              live=live,
              username=username,
              use_cache=use_cache,
              rate_key=f"football_api:{username or 'global'}",
          )
      finally:
          self._inflight.discard(cache_key)

  def _http_request(
      self,
      endpoint: str,
      clean_params: dict[str, Any],
      *,
      cache_key: str,
      ttl: int,
      feature: str,
      live: bool,
      username: str,
      use_cache: bool,
      rate_key: str,
  ) -> list[dict[str, Any]]:
      allowed, rate_msg = check_rate_limit(rate_key)
      if not allowed:
          stale = self._read_cache_any_age(cache_key) if use_cache else None
          if stale is not None:
              log_warning(f"Football internal rate limit — serving stale cache: {endpoint}")
              self._log_http_debug(
                  endpoint=endpoint,
                  params=clean_params,
                  status_code=200,
                  response_length=len(stale) if isinstance(stale, list) else 0,
                  cached=True,
                  error="internal_rate_limit_stale",
                  limiter="internal",
              )
              return stale
          self._log_http_debug(
              endpoint=endpoint,
              params=clean_params,
              status_code=None,
              response_length=0,
              cached=False,
              error="internal_rate_limit_block",
              limiter="internal",
          )
          raise FootballAPIError(rate_msg)

      url = f"{self.base_url}/{endpoint.lstrip('/')}"
      headers = {
          "x-apisports-key": FOOTBALL_API_KEY,
          "Accept": "application/json",
      }

      try:
          response = requests.get(
              url,
              headers=headers,
              params=clean_params,
              timeout=FOOTBALL_API_TIMEOUT,
          )
      except requests.Timeout as exc:
          log_error(f"Football API timeout: {endpoint} {clean_params}")
          raise FootballAPIError(
              "Football API Timeout. Bitte erneut versuchen."
          ) from exc
      except requests.RequestException as exc:
          log_error(f"Football API network error: {endpoint} -> {exc}")
          raise FootballAPIError(
              "Football API Netzwerkfehler. Bitte spaeter erneut versuchen."
          ) from exc

      rate_remaining = (
          response.headers.get("x-ratelimit-requests-remaining")
          or response.headers.get("X-RateLimit-Remaining")
      )
      dbg_headers = {
          "x-ratelimit-requests-limit": str(
              response.headers.get("x-ratelimit-requests-limit")
              or response.headers.get("X-RateLimit-Limit")
              or ""
          ),
          "x-ratelimit-requests-remaining": str(rate_remaining or ""),
          "x-ratelimit-requests-reset": str(
              response.headers.get("x-ratelimit-requests-reset")
              or response.headers.get("X-RateLimit-Reset")
              or ""
          ),
      }

      if response.status_code == 429:
          log_warning(f"Football API rate limit: {endpoint}")
          stale = self._read_cache_any_age(cache_key) if use_cache else None
          if stale is not None:
              log_warning(f"Football API 429 — serving stale cache: {endpoint}")
              self._log_http_debug(
                  endpoint=endpoint,
                  params=clean_params,
                  status_code=429,
                  response_length=len(stale) if isinstance(stale, list) else 0,
                  cached=True,
                  error="api_429_stale",
                  rate_limit_remaining=rate_remaining,
                  headers=dbg_headers,
                  response_snippet=str(getattr(response, "text", "") or "")[:1200],
                  limiter="api",
              )
              return stale
          self._log_http_debug(
              endpoint=endpoint,
              params=clean_params,
              status_code=429,
              response_length=0,
              cached=False,
              error="Football API Rate Limit erreicht",
              rate_limit_remaining=rate_remaining,
              headers=dbg_headers,
              response_snippet=str(getattr(response, "text", "") or "")[:1200],
              limiter="api",
          )
          raise FootballAPIError(
              "Football API Rate Limit erreicht. Bitte kurz warten oder Plan pruefen.",
              status_code=429,
          )

      try:
          payload = response.json()
      except ValueError as exc:
          log_error(f"Football API invalid JSON: {endpoint}")
          raise FootballAPIError("Ungueltige Football API Antwort.") from exc

      api_errors = self._parse_api_errors(payload)
      if api_errors:
          log_warning(f"Football API errors: {endpoint} -> {api_errors}")
          if isinstance(api_errors, dict):
              if api_errors.get("rateLimit"):
                  stale = self._read_cache_any_age(cache_key) if use_cache else None
                  if stale is not None:
                      self._log_http_debug(
                          endpoint=endpoint,
                          params=clean_params,
                          status_code=429,
                          response_length=len(stale) if isinstance(stale, list) else 0,
                          cached=True,
                          error=str(api_errors.get("rateLimit")),
                          rate_limit_remaining=rate_remaining,
                      )
                      return stale
                  raise FootballAPIError(
                      str(api_errors.get("rateLimit")),
                      status_code=429,
                      api_errors=api_errors,
                  )
              message = "; ".join(f"{k}: {v}" for k, v in api_errors.items())
          else:
              message = "; ".join(str(item) for item in api_errors)
          self._log_http_debug(
              endpoint=endpoint,
              params=clean_params,
              status_code=response.status_code,
              response_length=0,
              cached=False,
              error=message,
              rate_limit_remaining=rate_remaining,
              headers=dbg_headers,
              response_snippet=str(getattr(response, "text", "") or "")[:1200],
              limiter="api",
          )
          raise FootballAPIError(message or "Football API Fehler.", api_errors=api_errors)

      if response.status_code >= 400:
          self._log_http_debug(
              endpoint=endpoint,
              params=clean_params,
              status_code=response.status_code,
              response_length=0,
              cached=False,
              error=f"HTTP {response.status_code}",
              rate_limit_remaining=rate_remaining,
              headers=dbg_headers,
              response_snippet=str(getattr(response, "text", "") or "")[:1200],
              limiter="api",
          )
          raise FootballAPIError(
              f"Football API HTTP {response.status_code}",
              status_code=response.status_code,
          )

      data = payload.get("response") or []
      if not isinstance(data, list):
          data = [data] if data else []

      if use_cache:
          self._write_cache(cache_key, data)

      if username:
          try:
              record_api_success(username)
          except FootballAccessError as exc:
              raise FootballAPIError(str(exc)) from exc

      self._log_http_debug(
          endpoint=endpoint,
          params=clean_params,
          status_code=response.status_code,
          response_length=len(data),
          cached=False,
          rate_limit_remaining=rate_remaining,
          headers=dbg_headers,
          response_snippet=str(getattr(response, "text", "") or "")[:1200],
          limiter="api",
      )
      # Keep provider logs minimal in production.
      if self._dev_mode():
          log_info(f"Football API {endpoint} params={clean_params} results={len(data)}")
      return data

  def get_recent_fixtures(
      self,
      team_id: int,
      *,
      last_count: int = 5,
      username: str = "",
  ) -> list[dict[str, Any]]:
      return self._request(
          "fixtures",
          {"team": int(team_id), "last": max(1, min(int(last_count), 15))},
          feature="api_results",
          username=username,
      )

  def get_fixtures_by_league_season(
      self,
      league_id: int,
      *,
      season: int | None = None,
      username: str = "",
      ttl_override: int | None = None,
  ) -> list[dict[str, Any]]:
      """All fixtures for league+season (client-side date filter for upcoming)."""
      return self._request(
          "fixtures",
          {
              "league": int(league_id),
              "season": int(season or football_api_season() or FOOTBALL_DEFAULT_SEASON),
          },
          feature="api_fixtures",
          username=username,
          ttl_override=ttl_override,
      )

  def get_premium_fixtures_upcoming(
      self,
      *,
      days: int = 30,
      username: str = "",
  ) -> list[dict[str, Any]]:
      """
      Premium whitelist: fixtures?league=ID&season=current per league.
      From today through the next `days` days, sorted by kickoff.
      """
      from services.football_loaders import FINISHED_STATUSES, sort_fixtures_by_priority

      tz = ZoneInfo("Europe/Berlin")
      today = datetime.now(tz).date()
      horizon = today + timedelta(days=max(1, int(days)))
      seasons = football_api_seasons_to_try()

      # Composite cache: avoid re-fetching 12 leagues on every page load.
      composite_key = self._cache_key(
          "premium_upcoming",
          {"days": int(days), "core_ids": sorted(int(x) for x in FOOTBALL_BETTING_CORE_LEAGUE_IDS)},
      )
      composite_ttl = 21_600  # 6 hours
      cached = self._read_cache(composite_key, composite_ttl)
      if cached is not None:
          self._log_http_debug(
              endpoint="premium_upcoming",
              params={"days": int(days)},
              status_code=200,
              response_length=len(cached) if isinstance(cached, list) else 0,
              cached=True,
              limiter="cache",
          )
          return cached

      def _fixture_date_local(fx: dict[str, Any]) -> str:
          raw = str((fx.get("fixture") or {}).get("date") or "")
          if not raw:
              return ""
          try:
              normalized = raw.replace("Z", "+00:00")
              dt = datetime.fromisoformat(normalized)
              if dt.tzinfo is None:
                  dt = dt.replace(tzinfo=tz)
              return dt.astimezone(tz).date().isoformat()
          except ValueError:
              return raw[:10] if raw else ""

      def _in_window(fx: dict[str, Any]) -> bool:
          d_raw = _fixture_date_local(fx)
          if not d_raw:
              return False
          try:
              fx_date = datetime.fromisoformat(d_raw).date()
          except ValueError:
              return False
          if fx_date < today or fx_date > horizon:
              return False
          st = str(((fx.get("fixture") or {}).get("status") or {}).get("short") or "NS")
          return st not in FINISHED_STATUSES

      rows: list[dict[str, Any]] = []
      for lid in sorted(FOOTBALL_BETTING_CORE_LEAGUE_IDS):
          league_in_window: list[dict[str, Any]] = []
          for season in seasons:
              try:
                  part = self.get_fixtures_by_league_season(
                      int(lid),
                      season=season,
                      username=username,
                      ttl_override=21_600,
                  )
              except FootballAPIError:
                  continue
              if not part:
                  continue
              league_in_window = [fx for fx in part if _in_window(fx)]
              if league_in_window:
                  break
          rows.extend(league_in_window)

      seen: set[int] = set()
      deduped: list[dict[str, Any]] = []
      for fx in rows:
          fid = (fx.get("fixture") or {}).get("id")
          if not fid:
              continue
          try:
              key = int(fid)
          except (TypeError, ValueError):
              continue
          if key in seen:
              continue
          seen.add(key)
          deduped.append(fx)

      # Cache this "premium upcoming" path aggressively via TTL override.
      # It is the default data source on page load.
      out = sort_fixtures_by_priority(deduped)
      self._write_cache(composite_key, out)
      return out

  def get_live_fixtures(
      self,
      *,
      username: str = "",
      premium_only: bool = False,
  ) -> list[dict[str, Any]]:
      rows = self._request(
          "fixtures",
          {"live": "all"},
          feature="api_live_scores",
          live=True,
          username=username,
      )
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
  ) -> list[dict[str, Any]]:
      """Fixtures for YYYY-MM-DD, optional league filter."""
      params: dict[str, Any] = {"date": str(date).strip()[:10]}
      if league_id:
          params["league"] = int(league_id)
          params["season"] = int(season or football_api_season() or FOOTBALL_DEFAULT_SEASON)
      return self._request(
          "fixtures",
          params,
          feature="api_fixtures",
          live=False,
          username=username,
      )

  def get_fixture(self, fixture_id: int, *, username: str = "") -> dict[str, Any] | None:
      rows = self._request(
          "fixtures",
          {"id": int(fixture_id)},
          feature="api_fixtures",
          live=True,
          username=username,
      )
      return rows[0] if rows else None

  def get_head_to_head(
      self,
      team1_id: int,
      team2_id: int,
      *,
      last_count: int = 5,
      username: str = "",
  ) -> list[dict[str, Any]]:
      h2h = f"{int(team1_id)}-{int(team2_id)}"
      return self._request(
          "fixtures/headtohead",
          {"h2h": h2h, "last": max(1, min(int(last_count), 15))},
          feature="api_head_to_head",
          username=username,
      )

  def get_standings(
      self,
      league_id: int,
      *,
      season: int | None = None,
      username: str = "",
  ) -> list[dict[str, Any]]:
      return self._request(
          "standings",
          {
              "league": int(league_id),
              "season": int(season or FOOTBALL_DEFAULT_SEASON),
          },
          feature="api_standings",
          username=username,
      )

  def get_fixture_predictions(
      self,
      fixture_id: int,
      *,
      username: str = "",
  ) -> list[dict[str, Any]]:
      return self._request(
          "predictions",
          {"fixture": int(fixture_id)},
          feature="api_predictions",
          username=username,
      )

  def get_fixture_odds(
      self,
      fixture_id: int,
      *,
      username: str = "",
  ) -> list[dict[str, Any]]:
      """Bookmaker odds — separate /odds endpoint (not in fixtures)."""
      return self._request(
          "odds",
          {"fixture": int(fixture_id)},
          feature="ai_betting_intelligence",
          live=True,
          username=username,
      )

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
      """Injuries feed (cached 6h via _ttl_for)."""
      return self._request(
          "injuries",
          {
              "team": int(team_id),
              "season": int(season or FOOTBALL_DEFAULT_SEASON),
          },
          feature="api_injuries",
          username=username,
      )


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
