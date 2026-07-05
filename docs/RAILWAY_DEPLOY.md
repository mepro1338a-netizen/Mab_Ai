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

## WebSocket / „connection closed“ (1011, 1413, …)

Streamlit nutzt `/_stcore/stream` (WebSocket). Hinter Railway-Proxy können Browser-Meldungen wie **1011** (Internal Error) oder **1413 closed** (abnormale Schließung während Redeploy/Idle-Timeout) auftreten.

**Bereits im Repo:**

| Setting | Wo |
|---------|-----|
| `enableCORS = false` | `.streamlit/config.toml`, `start.sh`, `main.py` |
| `enableXsrfProtection = false` | wie oben |
| `enableWebsocketCompression = false` | wie oben (Proxy strippt oft `Sec-WebSocket-Extensions`) |
| `websocketPingInterval = 25` | `.streamlit/config.toml`, `start.sh` (Streamlit ≥1.48) |
| Kein festes `port` in config | Port nur via Railway `$PORT` / `start.sh` |

**Railway Variables prüfen:**

```env
APP_BASE_URL=https://mabyte.de   # exakt die öffentliche Domain, HTTPS, kein Markdown
DATA_DIR=/data                   # Volume mount
```

`APP_BASE_URL` ist für OAuth/Stripe — fehlt oder ist falsch, bricht Redirects; bei WebSocket-Problemen nach Redeploy: **Hard Refresh** (Ctrl+Shift+R) oder Tab neu öffnen.

**Checkliste nach Deploy:**

1. Railway → Variables → `APP_BASE_URL` = finale Domain
2. Volume auf `/data`, `DATA_DIR=/data`
3. Build grün, `GET /_stcore/health` → 200
4. Browser Hard Refresh; bei anhaltendem Fehler Inkognito testen
