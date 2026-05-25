# MaByte Deployment (Railway / Production)

## Entry
```bash
streamlit run main.py --server.port $PORT --server.address 0.0.0.0
```
Railway nutzt `start.sh` / `railway.toml` mit Healthcheck `/_stcore/health`.

## Build
- Python 3.11+
- `pip install -r requirements.txt`
- Kein `init_db()` beim Import — nur `ensure_db_ready()` in `main.py` / `ui.py`

## Railway Variables (Minimum)
| Variable | Beispiel |
|----------|----------|
| `APP_BASE_URL` | `https://mabyte.de` |
| `DATA_DIR` | `/data` |
| `OAUTH_STATE_SECRET` | langer Zufallsstring |
| `GOOGLE_CLIENT_ID` / `SECRET` | Google Console |
| `OPENAI_API_KEY` | optional für AI |
| `FOOTBALL_API_KEY` | api-sports.io |
| `STRIPE_SECRET_KEY` | Live/Test |
| `STRIPE_PRICE_*` | Price IDs |

Vollständige Liste: `ENV_SETUP.md`

## Volume
Mount `/data` für persistente SQLite (`mabai.db`) und Football-Cache.

## Deploy Steps
1. Push zu Railway-connected Repo
2. Env prüfen (`ENV_SETUP.md`)
3. Deploy abwarten (Healthcheck bis 300s)
4. Manuell: Login, Premium, Football, Support, Admin

## Rollback
Railway: vorheriges Deployment reaktivieren — DB auf Volume bleibt erhalten.

## Custom Domain
`mabyte.de` → `APP_BASE_URL` und Google OAuth Redirect müssen identisch sein.
