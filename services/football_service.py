"""Football live-data client for API-Football (api-sports.io)."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

import requests

from config import (
    DATA_DIR,
    FOOTBALL_API_BASE_URL,
    FOOTBALL_API_CACHE_TTL,
    FOOTBALL_API_KEY,
    FOOTBALL_API_LIVE_CACHE_TTL,
    FOOTBALL_API_TIMEOUT,
    FOOTBALL_DEFAULT_SEASON,
)
from logger import log_error, log_info, log_warning
from security import check_rate_limit
from services.football_access import (
    FootballAccessError,
    football_priority_cache,
    preflight_api_request,
    record_api_success,
    resolve_football_plan,
)


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
      if live or endpoint in {"fixtures", "fixtures/statistics"}:
          base = max(15, int(FOOTBALL_API_LIVE_CACHE_TTL))
      else:
          base = max(30, int(FOOTBALL_API_CACHE_TTL))
      if username and football_priority_cache(resolve_football_plan(username)):
          return max(15, base // 2)
      return base

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
      ttl = self._ttl_for(endpoint, live, username)

      if use_cache:
          cached = self._read_cache(cache_key, ttl)
          if cached is not None:
              return cached

      rate_key = f"football_api:{username or 'global'}"
      allowed, rate_msg = check_rate_limit(rate_key)
      if not allowed:
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

      if response.status_code == 429:
          log_warning(f"Football API rate limit: {endpoint}")
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
                  raise FootballAPIError(
                      str(api_errors.get("rateLimit")),
                      status_code=429,
                      api_errors=api_errors,
                  )
              message = "; ".join(f"{k}: {v}" for k, v in api_errors.items())
          else:
              message = "; ".join(str(item) for item in api_errors)
          raise FootballAPIError(message or "Football API Fehler.", api_errors=api_errors)

      if response.status_code >= 400:
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

      log_info(
          f"Football API {endpoint} params={clean_params} results={len(data)}"
      )
      return data

  def search_teams(self, name: str, *, username: str = "") -> list[dict[str, Any]]:
      query = (name or "").strip()
      if len(query) < 2:
          raise FootballAPIError("Bitte mindestens 2 Zeichen fuer die Teamsuche eingeben.")
      return self._request(
          "teams",
          {"search": query},
          feature="api_team_overview",
          username=username,
      )

  def get_team(self, team_id: int, *, username: str = "") -> dict[str, Any] | None:
      rows = self._request(
          "teams",
          {"id": int(team_id)},
          feature="api_team_overview",
          username=username,
      )
      return rows[0] if rows else None

  def get_upcoming_fixtures(
      self,
      team_id: int,
      *,
      next_count: int = 5,
      username: str = "",
  ) -> list[dict[str, Any]]:
      return self._request(
          "fixtures",
          {"team": int(team_id), "next": max(1, min(int(next_count), 15))},
          feature="api_fixtures",
          username=username,
      )

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

  def get_league_upcoming_fixtures(
      self,
      league_id: int,
      *,
      next_count: int = 10,
      season: int | None = None,
      username: str = "",
  ) -> list[dict[str, Any]]:
      return self._request(
          "fixtures",
          {
              "league": int(league_id),
              "season": int(season or FOOTBALL_DEFAULT_SEASON),
              "next": max(1, min(int(next_count), 20)),
          },
          feature="api_fixtures",
          username=username,
      )

  def get_league_recent_fixtures(
      self,
      league_id: int,
      *,
      last_count: int = 10,
      season: int | None = None,
      username: str = "",
  ) -> list[dict[str, Any]]:
      return self._request(
          "fixtures",
          {
              "league": int(league_id),
              "season": int(season or FOOTBALL_DEFAULT_SEASON),
              "last": max(1, min(int(last_count), 20)),
          },
          feature="api_results",
          username=username,
      )

  def get_live_fixtures(self, *, username: str = "") -> list[dict[str, Any]]:
      return self._request(
          "fixtures",
          {"live": "all"},
          feature="api_live_scores",
          live=True,
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

  def get_fixture_statistics(
      self,
      fixture_id: int,
      *,
      username: str = "",
  ) -> list[dict[str, Any]]:
      return self._request(
          "fixtures/statistics",
          {"fixture": int(fixture_id)},
          feature="api_player_stats",
          live=True,
          username=username,
      )

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

  def get_team_injuries(
      self,
      team_id: int,
      *,
      season: int | None = None,
      username: str = "",
  ) -> list[dict[str, Any]]:
      return self._request(
          "injuries",
          {
              "team": int(team_id),
              "season": int(season or FOOTBALL_DEFAULT_SEASON),
          },
          feature="api_injuries",
          username=username,
      )

  def search_leagues(
      self,
      name: str,
      *,
      country: str = "",
      username: str = "",
  ) -> list[dict[str, Any]]:
      query = (name or "").strip()
      if len(query) < 2:
          raise FootballAPIError("Bitte mindestens 2 Zeichen fuer die Ligasuche eingeben.")
      params: dict[str, Any] = {"search": query}
      if country.strip():
          params["country"] = country.strip()
      return self._request(
          "leagues",
          params,
          feature="api_multi_league",
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


def team_display_name(team_row: dict[str, Any]) -> str:
  team = team_row.get("team") or {}
  country = team_row.get("country") or team.get("country") or ""
  name = team.get("name") or "Team"
  if country:
      return f"{name} ({country})"
  return name


def fixture_team_names(fixture: dict[str, Any]) -> tuple[str, str]:
  teams = fixture.get("teams") or {}
  home = (teams.get("home") or {}).get("name") or ""
  away = (teams.get("away") or {}).get("name") or ""
  return home, away


def format_fixture_stats(stats_rows: list[dict[str, Any]]) -> str:
  if not stats_rows:
      return "Keine Statistiken verfuegbar."

  lines: list[str] = []
  for block in stats_rows:
      team_name = ((block.get("team") or {}).get("name") or "Team")
      lines.append(f"### {team_name}")
      for item in block.get("statistics") or []:
          stat_type = item.get("type") or "Stat"
          value = item.get("value")
          lines.append(f"- **{stat_type}:** {value}")
      lines.append("")
  return "\n".join(lines).strip()


_service: FootballService | None = None


def get_football_service() -> FootballService:
  global _service
  if _service is None:
      _service = FootballService()
  return _service
