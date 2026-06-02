# Railway Production — MaByte

## Startbefehl (automatisch via `railway.toml`)

```bash
sh start.sh
```

Entspricht:

```bash
streamlit run main.py --server.port $PORT --server.address 0.0.0.0
```

## Einstiegspunkt

| Datei | Rolle |
|-------|--------|
| `main.py` | **Production entry** — PORT, Logging, DB bootstrap, lädt `ui.py` |
| `ui.py` | Streamlit App (Seiten, Router) |
| `start.sh` | Shell-Wrapper für Railway `$PORT` |
| `railway.toml` | Start + Healthcheck |

## Healthcheck

Railway prüft: `GET /_stcore/health` (Streamlit built-in)

Lokal (wenn App läuft):

```bash
python logger.py --healthcheck --http
```

## Pflicht-ENV (Production)

```env
PORT=<von Railway gesetzt>
APP_BASE_URL=https://mabyte.de
DATA_DIR=/data
```

Optional aber empfohlen: `OPENAI_API_KEY`, `GOOGLE_*`, `OAUTH_STATE_SECRET`, `STRIPE_*`, `FOOTBALL_API_KEY`

Fehlende Keys crashen die App **nicht** — Features zeigen Hinweise.

## Custom Domain (mabyte.de)

1. Railway → Service → Settings → Custom Domain → `mabyte.de`
2. `APP_BASE_URL=https://mabyte.de` in Variables
3. DNS CNAME auf Railway zeigen lassen

## Volume (empfohlen)

Mount `/data` und setze `DATA_DIR=/data` damit SQLite über Redeploys erhalten bleibt.

## Timeout-Fixes

- Kein `init_db()` mehr beim Import (schnellerer Cold Start)
- `ensure_db_ready()` einmal in `main.py` + idempotent in `ui.py`
- `psycopg2` aus requirements entfernt (nicht genutzt, längere Builds)
- Healthcheck Timeout 300s in `railway.toml`
