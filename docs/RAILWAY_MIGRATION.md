# Railway-Migration — MaByte auf neues Konto

Anleitung zum **Neu-Anlegen** des MaByte-Projekts auf dem Railway-Konto **maksigewinnt@gmail.com**, während das GitHub-Repo unverändert bleibt.

> **Wichtig:** Railway-Projekte lassen sich **nicht** zwischen E-Mail-Konten übertragen. Du erstellst ein **neues Projekt** auf dem Zielkonto und verbindest dasselbe GitHub-Repo erneut.

**GitHub-Repo (unverändert):** [mepro1338a-netizen/Mab_Ai](https://github.com/mepro1338a-netizen/Mab_Ai)

---

## Übersicht

| Was | Aktion |
|-----|--------|
| GitHub-Repo | Bleibt bei `mepro1338a-netizen` |
| Railway-Konto | Neu: `maksigewinnt@gmail.com` |
| Altes Railway-Projekt | Nach erfolgreichem Cutover löschen / trennen |
| Secrets / API-Keys | Manuell aus altem Projekt kopieren (Railway UI oder lokale `.env`) — **niemals ins Repo committen** |

### Services in diesem Repo

| Service | Config | Start | Healthcheck |
|---------|--------|-------|-------------|
| **Streamlit (Haupt-App)** | `railway.toml` + `Dockerfile` | `sh start.sh` | `/_stcore/health` |
| **Football AI API** (optional) | `railway.api.toml` | `sh start_api.sh` | `/health` |
| **Stripe Webhook** (optional) | `railway.webhook.toml` + `Dockerfile.webhook` | `sh start-webhook.sh` | `/healthz` |

Weitere Details zur Football-API: [`docs/RAILWAY_API.md`](RAILWAY_API.md)  
Allgemeines Deploy: [`docs/RAILWAY_DEPLOY.md`](RAILWAY_DEPLOY.md)

---

## Voraussetzungen & mögliche Blocker

### 1. GitHub-Zugriff für das neue Railway-Konto

Railway verbindet sich per **GitHub OAuth**. Das Konto `maksigewinnt@gmail.com` muss das Repo sehen können:

- **Option A:** GitHub-User `maksigewinnt` (oder verknüpfter Account) ist **Collaborator** am Repo `mepro1338a-netizen/Mab_Ai`
- **Option B:** Beide Accounts gehören derselben **GitHub-Organisation** mit Repo-Zugriff

Ohne Zugriff erscheint das Repo in Railway nicht unter „Deploy from GitHub“.

**Prüfen (Repo-Besitzer):**

```bash
gh repo view mepro1338a-netizen/Mab_Ai --json url
# Collaborator hinzufügen (falls nötig):
# gh api repos/mepro1338a-netizen/Mab_Ai/collaborators/<github-username> -X PUT
```

### 2. DNS & Custom Domain

Wenn `mabyte.de` noch auf das **alte** Railway-Projekt zeigt:

1. Erst neues Projekt deployen und testen (Railway-Standarddomain)
2. Dann CNAME/Custom Domain im **neuen** Service setzen
3. Alte Domain im alten Projekt entfernen, bevor du das alte Projekt löschst

### 3. Externe Redirect-URIs aktualisieren

Nach Domain-Wechsel anpassen in:

- **Google Cloud Console** → OAuth Redirect URIs (`GOOGLE_OAUTH_REDIRECT_URI` / `APP_BASE_URL`)
- **Meta / TikTok Developer Console** → Redirect URLs
- **Stripe Dashboard** → Webhook-Endpoint-URL (falls Stripe-Webhook-Service genutzt)

---

## Schritt-für-Schritt

### Schritt 1 — Bei Railway anmelden

1. [railway.app](https://railway.app) öffnen
2. Mit **maksigewinnt@gmail.com** einloggen (nicht das alte Konto)
3. Optional lokal: `railway login` (CLI muss danach `railway whoami` das richtige Konto zeigen)

### Schritt 2 — Neues Projekt aus GitHub

1. **New Project** → **Deploy from GitHub repo**
2. GitHub-App autorisieren (falls noch nicht geschehen) — Zugriff auf `mepro1338a-netizen/Mab_Ai` erlauben
3. Repo **Mab_Ai** auswählen, Branch **`main`**
4. Railway erstellt automatisch den ersten Service (Streamlit)

Der erste Service nutzt standardmäßig `railway.toml` im Repo-Root:

```toml
# railway.toml — Streamlit
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "sh start.sh"
healthcheckPath = "/_stcore/health"
```

### Schritt 3 — Service 1: Streamlit (Haupt-App)

**Settings prüfen:**

| Einstellung | Wert |
|-------------|------|
| Config file | `railway.toml` (Default) |
| Start Command | `sh start.sh` |
| Builder | Dockerfile (`Dockerfile`) |

**Volume (empfohlen):**

1. Service → **Volumes** → Mount **`/data`**
2. Variable setzen: `DATA_DIR=/data` (SQLite bleibt über Redeploys erhalten)

**Networking:**

1. **Generate Domain** (z. B. `mab-ai-production.up.railway.app`)
2. Optional: **Custom Domain** `mabyte.de` (erst nach Test der Standarddomain)

**Variables:** Alle Variablen aus Abschnitt [Streamlit — Variablen-Checkliste](#streamlit--variablen-checkliste) setzen.

Mindestens:

```env
APP_BASE_URL=https://<deine-neue-railway-domain>
DATA_DIR=/data
```

`PORT` wird von Railway automatisch gesetzt — **nicht manuell überschreiben**.

### Schritt 4 — Service 2: Football AI API (optional)

Nur nötig, wenn die Streamlit-App `FOOTBALL_AI_API_URL` nutzt (separater FastAPI-Service).

1. Im **selben Railway-Projekt** → **New Service** → **GitHub Repo** → wieder `Mab_Ai`
2. **Settings → Config file:** `railway.api.toml`
3. **Start Command:** `sh start_api.sh` (falls nicht aus TOML übernommen)
4. **Networking → Generate Domain** (z. B. `football-ai-production.up.railway.app`)
5. Variables aus [Football API — Variablen-Checkliste](#football-api--variablen-checkliste) setzen
6. Im **Streamlit-Service** setzen:

```env
FOOTBALL_AI_API_URL=https://<football-api-domain>
```

7. Auf dem API-Service `API_CORS_ORIGINS` auf die Streamlit-Domain(s) setzen:

```env
API_CORS_ORIGINS=https://<streamlit-domain>,https://mabyte.de
```

Details: [`docs/RAILWAY_API.md`](RAILWAY_API.md)

### Schritt 5 — Service 3: Stripe Webhook (optional)

Falls Stripe-Webhooks über einen separaten Service laufen:

1. **New Service** → GitHub Repo `Mab_Ai`
2. **Config file:** `railway.webhook.toml`
3. **Dockerfile:** `Dockerfile.webhook`
4. **Start:** `sh start-webhook.sh`
5. Domain generieren, Endpoint in Stripe Dashboard eintragen
6. `STRIPE_WEBHOOK_SECRET` auf **allen** Services setzen, die Webhooks verarbeiten

### Schritt 6 — Variablen vom alten Projekt kopieren

Im **alten** Railway-Projekt: **Variables** → Werte manuell kopieren (oder aus lokaler `.env`, falls vorhanden).

**Regeln:**

- Keine Secrets ins Git committen
- API-Keys, die in Chats/Logs aufgetaucht sind → **rotieren** und nur in Railway setzen
- Nach Migration: alte Railway-Variablen als obsolet betrachten

### Schritt 7 — Domains & `APP_BASE_URL` finalisieren

1. Streamlit-Service: öffentliche URL notieren
2. `APP_BASE_URL` auf finale URL setzen (Railway-Domain oder `https://mabyte.de`)
3. Custom Domain DNS (CNAME) auf neues Railway-Projekt umstellen
4. OAuth-Provider & Stripe Webhooks mit neuer URL aktualisieren
5. Redeploy auslösen (Push auf `main` oder **Redeploy** in Railway)

### Schritt 8 — Altes Railway-Projekt trennen

**Erst nach erfolgreichem Test** des neuen Deployments:

1. Custom Domain im **alten** Projekt entfernen
2. Altes Projekt → **Settings → Danger** → **Delete Project**
3. Optional: GitHub-Integration des alten Kontos vom Repo trennen (GitHub → Settings → Applications → Railway)

---

## Variablen-Checklisten (Namen only)

### Automatisch (Railway)

| Variable | Hinweis |
|----------|---------|
| `PORT` | Von Railway gesetzt |
| `RAILWAY_*` | Von Railway injiziert (Environment, Domain, …) |

### Streamlit — Pflicht / empfohlen

| Variable | Pflicht | Beschreibung |
|----------|---------|--------------|
| `APP_BASE_URL` | **Ja** | Öffentliche App-URL (OAuth, Stripe Redirects) |
| `DATA_DIR` | Empfohlen | `/data` mit Volume-Mount |
| `OPENAI_API_KEY` | Empfohlen | Kern-AI-Features |

### Streamlit — OAuth

| Variable |
|----------|
| `GOOGLE_CLIENT_ID` |
| `GOOGLE_CLIENT_SECRET` |
| `GOOGLE_OAUTH_REDIRECT_URI` |
| `GOOGLE_OAUTH_REDIRECT_PATH` |
| `YOUTUBE_OAUTH_CLIENT_ID` |
| `YOUTUBE_OAUTH_CLIENT_SECRET` |
| `META_APP_ID` |
| `META_APP_SECRET` |
| `TIKTOK_CLIENT_KEY` |
| `TIKTOK_CLIENT_SECRET` |
| `OAUTH_STATE_SECRET` |
| `VIDEO_TOKEN_ENCRYPT_KEY` |

### Streamlit — Stripe

| Variable |
|----------|
| `STRIPE_SECRET_KEY` |
| `STRIPE_WEBHOOK_SECRET` |
| `STRIPE_SUCCESS_URL` |
| `STRIPE_PRICE_PRO` |
| `STRIPE_PRICE_GRAND` |
| `STRIPE_PRICE_ELITE` |
| `STRIPE_PRICE_FOOTBALL_STARTER` |
| `STRIPE_PRICE_FOOTBALL_PRO` |
| `STRIPE_PRICE_FOOTBALL_ELITE` |

### Streamlit — OpenAI / Media

| Variable |
|----------|
| `OPENAI_API_KEY` |
| `OPENAI_TEXT_MODEL` |
| `OPENAI_CODING_MODEL` |
| `OPENAI_IMAGE_MODEL` |
| `OPENAI_FREE_MODEL` |
| `OPENAI_PRO_MODEL` |
| `OPENAI_GRAND_MODEL` |
| `OPENAI_ELITE_MODEL` |
| `IMAGE_PROVIDER` |
| `VIDEO_PROVIDER` |
| `MUSIC_PROVIDER` |
| `STABILITY_API_KEY` |
| `STABILITY_IMAGE_MODEL` |
| `REPLICATE_API_TOKEN` |
| `REPLICATE_VIDEO_MODEL` |
| `VIDEO_MODEL` |
| `REPLICATE_REELS_MODEL` |
| `REPLICATE_MUSIC_MODEL` |
| `FAL_KEY` |
| `FAL_VIDEO_ENDPOINT` |
| `FAL_MUSIC_ENDPOINT` |

### Streamlit — Football (Daten + optional API-URL)

| Variable |
|----------|
| `FOOTBALL_AI_API_URL` |
| `FOOTBALL_API_PROVIDER` |
| `FOOTBALL_DATA_API_KEY` |
| `FOOTBALL_DATA_BASE_URL` |
| `FOOTBALL_DATA_TIMEOUT` |
| `FOOTBALL_DATA_CACHE_TTL` |
| `FOOTBALL_DATA_LIVE_CACHE_TTL` |
| `FOOTBALL_DATA_STANDINGS_CACHE_TTL` |
| `FOOTBALL_API_INCLUDE` |
| `SPORTMONKS_API_KEY` |
| `SPORTMONKS_BASE_URL` |
| `FOOTBALL_DEFAULT_SEASON` |
| `FOOTBALL_AI_CACHE_TTL` |

### Streamlit — Optional / Legacy

| Variable | Hinweis |
|----------|---------|
| `FOOTBALL_API_KEY` | Deprecated (api-sports.io) |
| `FOOTBALL_API_BASE_URL` | Deprecated |
| `FOOTBALL_API_CACHE_TTL` | Deprecated |
| `FOOTBALL_API_LIVE_CACHE_TTL` | Deprecated |
| `FOOTBALL_API_FIXTURES_CACHE_TTL` | Deprecated |
| `FOOTBALL_API_STANDINGS_CACHE_TTL` | Deprecated |
| `FOOTBALL_API_INJURIES_CACHE_TTL` | Deprecated |
| `FOOTBALL_API_TIMEOUT` | Deprecated |
| `RESEND_API_KEY` | E-Mail (optional) |
| `EMAIL_FROM` | E-Mail (optional) |
| `SUNO_API_URL` | Optional |
| `SUNO_API_KEY` | Optional |
| `MABYTE_ENV` | z. B. `production` |
| `MABYTE_DEBUG` | Debug-Logging |
| `DEV_MODE` | Entwicklung |

### Football API — Variablen-Checkliste

Mindestens ein Provider-Key je nach `FOOTBALL_API_PROVIDER`:

| Variable | Pflicht |
|----------|---------|
| `FOOTBALL_API_PROVIDER` | Nein (Default: `football-data.org`) |
| `FOOTBALL_DATA_API_KEY` | Ja*, wenn Provider = `football-data.org` |
| `SPORTMONKS_API_KEY` | Ja*, wenn Provider = `sportmonks` |
| `API_CORS_ORIGINS` | Empfohlen (Streamlit-Domains) |
| `FOOTBALL_API_INCLUDE` | Nein |
| `SPORTMONKS_BASE_URL` | Nein |
| `FOOTBALL_AI_CACHE_TTL` | Nein |
| `FOOTBALL_DATA_CACHE_TTL` | Nein |
| `FOOTBALL_DATA_LIVE_CACHE_TTL` | Nein |
| `FOOTBALL_DATA_STANDINGS_CACHE_TTL` | Nein |
| `FOOTBALL_DATA_TIMEOUT` | Nein |
| `FOOTBALL_DEFAULT_SEASON` | Nein |
| `APP_BASE_URL` | Fallback für CORS, wenn `API_CORS_ORIGINS` leer |

Quelle der Football-Env-Logik: `core/config.py` (Single Source of Truth).

### Stripe Webhook-Service

| Variable |
|----------|
| `STRIPE_SECRET_KEY` |
| `STRIPE_WEBHOOK_SECRET` |
| `PORT` (auto) |

---

## Verifikation nach Migration

```bash
# Streamlit Health (Railway-Domain)
curl -sS https://<streamlit-domain>/_stcore/health

# Football API (falls aktiv)
curl -sS https://<football-api-domain>/health

# Lokal CLI (optional)
railway whoami
railway status
```

In der App (Admin-Bereich): Railway-Environment, Domain und konfigurierte Keys prüfen.

---

## Kurz-Checkliste

- [ ] Railway als `maksigewinnt@gmail.com` eingeloggt
- [ ] GitHub-Zugriff auf `mepro1338a-netizen/Mab_Ai` für Railway OAuth
- [ ] Neues Projekt + Streamlit-Service deployed (`railway.toml`)
- [ ] Volume `/data` + `DATA_DIR=/data`
- [ ] Alle Variables kopiert (keine Secrets committed)
- [ ] Domain generiert, `APP_BASE_URL` aktualisiert
- [ ] Optional: Football-API-Service + `FOOTBALL_AI_API_URL` + `API_CORS_ORIGINS`
- [ ] OAuth / Stripe Redirects & Webhooks auf neue URLs
- [ ] DNS `mabyte.de` auf neues Projekt (wenn genutzt)
- [ ] Altes Railway-Projekt gelöscht / getrennt

---

## Referenz — Repo-Dateien

| Datei | Rolle |
|-------|--------|
| `railway.toml` | Streamlit Build & Deploy |
| `railway.api.toml` | Football FastAPI Service |
| `railway.webhook.toml` | Stripe Webhook Service |
| `Dockerfile` | Streamlit Container |
| `start.sh` | `streamlit run main.py` auf `$PORT` |
| `start_api.sh` | `uvicorn main:app` auf `$PORT` |
| `start-webhook.sh` | Stripe Webhook Handler |
| `Procfile` | `web: sh start.sh` (Heroku-kompatibel) |
| `.env.example` | Lokale Vorlage aller Variablen |
| `config.py` / `core/config.py` | Env-Reader in der App |
