# Railway — Football AI API (zweiter Service)

Separater FastAPI-Service neben der Streamlit-App. Gleiches Repo, eigene Railway-Service-Instanz.

## 1. Neuen Service anlegen

1. Railway-Projekt öffnen → **New Service** → **GitHub Repo** (dieses Repo).
2. **Settings → Config file:** `railway.api.toml`
3. **Settings → Start Command** (falls nicht aus TOML): `sh start_api.sh`
4. **Networking → Generate Domain** (z. B. `football-ai-production.up.railway.app`)

Der Streamlit-Service bleibt unverändert (`railway.toml` + `Dockerfile`).

## 2. Umgebungsvariablen (API-Service)

| Variable | Pflicht | Beschreibung |
|----------|---------|--------------|
| `FOOTBALL_DATA_API_KEY` | **Ja** | Key von [football-data.org](https://www.football-data.org/client/register) |
| `API_CORS_ORIGINS` | Empfohlen | Komma-getrennte Streamlit-Origins, z. B. `https://mabai-production.up.railway.app,https://mabyte.de` |
| `FOOTBALL_AI_CACHE_TTL` | Nein | Tip-Cache in Sekunden (Default: `900`) |
| `FOOTBALL_DATA_CACHE_TTL` | Nein | football-data.org Cache (Default: `21600`) |
| `PORT` | Auto | Von Railway gesetzt — nicht manuell setzen |

`PORT` wird von Railway gesetzt. `start_api.sh` startet:

```bash
uvicorn api.app:app --host 0.0.0.0 --port "$PORT"
```

## 3. Umgebungsvariablen (Streamlit-Service)

| Variable | Beschreibung |
|----------|--------------|
| `FOOTBALL_AI_API_URL` | Öffentliche API-URL, z. B. `https://football-ai-production.up.railway.app` (für künftige UI-Anbindung) |
| `FOOTBALL_DATA_API_KEY` | Kann auf Streamlit bleiben (lokale Football-Features); API-Service braucht eigenen Key |

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
| `start_api.sh` | Start mit Railway `$PORT` |
| `railway.api.toml` | Build (Nixpacks) + Healthcheck |
| `Procfile.api` | Alternative Start-Definition |
| `api/app.py` | FastAPI-App |
| `core/config.py` | API-Settings (Pydantic) |
