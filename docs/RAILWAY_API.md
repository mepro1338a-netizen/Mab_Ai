# Railway — Football AI API (zweiter Service)

Separater FastAPI-Service neben der Streamlit-App. Gleiches Repo, eigene Railway-Service-Instanz.

## 1. Neuen Service anlegen

1. Railway-Projekt öffnen → **New Service** → **GitHub Repo** (dieses Repo).
2. **Settings → Config file:** `railway.api.toml`
3. **Settings → Start Command** (falls nicht aus TOML): `sh start_api.sh`
4. **Networking → Generate Domain** (z. B. `football-ai-production.up.railway.app`)

Der Streamlit-Service bleibt unverändert (`railway.toml` + `Dockerfile`).

## 2. Umgebungsvariablen (API-Service)

### Provider wählen

| `FOOTBALL_API_PROVIDER` | Quelle | Erforderlicher Key |
|-------------------------|--------|-------------------|
| `football-data.org` (Default) | [football-data.org v4](https://www.football-data.org/client/register) | `FOOTBALL_DATA_API_KEY` |
| `sportmonks` | [SportMonks Football API v3](https://www.sportmonks.com/) | `SPORTMONKS_API_KEY` |

| Variable | Pflicht | Beschreibung |
|----------|---------|--------------|
| `FOOTBALL_API_PROVIDER` | Nein | `football-data.org` (Default) oder `sportmonks` |
| `FOOTBALL_DATA_API_KEY` | Ja* | football-data.org Token (* wenn Provider = football-data.org) |
| `SPORTMONKS_API_KEY` | Ja* | SportMonks Token (* wenn Provider = sportmonks) |
| `FOOTBALL_API_INCLUDE` | Nein | SportMonks `include`-Parameter (Default: `participants;scores;periods;events;league.country;round`) |
| `SPORTMONKS_BASE_URL` | Nein | Default: `https://api.sportmonks.com/v3/football` |
| `API_CORS_ORIGINS` | Empfohlen | Komma-getrennte Streamlit-Origins, z. B. `https://mabai-production.up.railway.app,https://mabyte.de` |
| `FOOTBALL_AI_CACHE_TTL` | Nein | Tip-Cache in Sekunden (Default: `900`) |
| `FOOTBALL_DATA_CACHE_TTL` | Nein | Fixture-Cache (Default: `21600`) |
| `PORT` | Auto | Von Railway gesetzt — nicht manuell setzen |

`PORT` wird von Railway gesetzt. `start_api.sh` startet:

```bash
uvicorn main:app --host 0.0.0.0 --port "$PORT"
```

Ohne passenden API-Key bricht der API-Service beim Start ab (`RuntimeError` in der FastAPI-Lifespan — Streamlit bleibt unberührt).

### Secret Management

| Regel | Umsetzung |
|-------|-----------|
| Einziger Env-Reader | `core/config.py` liest `FOOTBALL_*` / `SPORTMONKS_*` via `os.getenv` |
| Services | `football_data_client.py` / `sportmonks_client.py` nutzen Getter aus `core.config` — kein direktes `os.getenv` |
| Streamlit | Root-`config.py` re-exportiert aus `core.config` (kein zweites Lesen) |
| Startup-Check | `require_football_data_api_key()` in `api/app.py` Lifespan — prüft Provider + Key |
| Keine Hardcodes | **Kein Token im Repo.** Nur in Railway Variables oder lokale `.env` (gitignored) |
| Token-Rotation | Token, die in Chats/Logs auftauchen, sofort rotieren und nur in Railway/.env setzen |

## 3. Umgebungsvariablen (Streamlit-Service)

| Variable | Beschreibung |
|----------|--------------|
| `FOOTBALL_AI_API_URL` | Öffentliche API-URL, z. B. `https://football-ai-production.up.railway.app` |
| `FOOTBALL_API_PROVIDER` | Gleicher Provider wie API-Service |
| `FOOTBALL_DATA_API_KEY` | football-data.org Key (wenn Provider = football-data.org) |
| `SPORTMONKS_API_KEY` | SportMonks Key (wenn Provider = sportmonks) |
| `FOOTBALL_API_INCLUDE` | Optional — SportMonks Includes (siehe oben) |

## 4. Healthcheck

Railway prüft: `GET /health`

```json
{"status": "ok", "football_api_configured": true}
```

Lokal:

```bash
sh start_api.sh
curl http://localhost:8000/health
```

## 5. API-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| `GET` | `/health` | Healthcheck |
| `GET` | `/ai/tips/today` | Heutige AI-Tipps |
| `GET` | `/ai/match-analysis/{home_id}/{away_id}` | Match-Analyse |
| `GET` | `/ai/team-form/{team_id}` | Team-Form |

OpenAPI-Docs: `https://<api-domain>/docs`

## 6. CORS

Nur konfigurierte Origins sind erlaubt (kein offenes `*` in Production).

Setze auf dem **API-Service**:

```env
API_CORS_ORIGINS=https://mabai-production.up.railway.app,https://mabyte.de
```

Ohne `API_CORS_ORIGINS` gilt `APP_BASE_URL` als Fallback (falls auf dem API-Service gesetzt).

## 7. Dateien

| Datei | Rolle |
|-------|--------|
| `main.py` | FastAPI-Einstieg (`app` re-export) + Streamlit bei `streamlit run main.py` |
| `start_api.sh` | Start mit Railway `$PORT` (`uvicorn main:app`) |
| `railway.api.toml` | Build (Nixpacks) + Healthcheck |
| `Procfile.api` | Alternative Start-Definition |
| `api/app.py` | FastAPI-App-Factory + Startup-Key-Check |
| `core/config.py` | Provider-Settings + `require_football_data_api_key()` |
| `services/football_data_client.py` | football-data.org HTTP + Mapper |
| `services/sportmonks_client.py` | SportMonks HTTP + Mapper |
