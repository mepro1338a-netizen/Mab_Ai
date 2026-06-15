# Datenbank-Migration — SQLite von altem zu neuem Railway

MaByte speichert **alle** App-Daten in einer SQLite-Datei:

```text
{DATA_DIR}/mabai.db
```

Production: `DATA_DIR=/data` mit Railway-Volume-Mount auf `/data`.

| Deployment | URL (Stand Migration) |
|------------|------------------------|
| **Alt** | `https://mabai-production.up.railway.app` (altes Railway-Konto) |
| **Neu** | `https://web-production-734b0.up.railway.app` (maksigewinnt@gmail.com) |

> **Kein PostgreSQL:** Es gibt keine `DATABASE_URL`. Nur `mabai.db` auf dem Volume kopieren oder per SQL-Dump importieren.

---

## Woher kommen die alten Daten?

| Quelle | Wann nutzen |
|--------|-------------|
| **A — Volume im alten Railway-Projekt** | Produktionsdaten (User, Payments, Tickets, …) — **primäre Quelle** |
| **B — Lokale Kopie** `data/mabai.db` | Nur wenn du die DB schon vom alten Server exportiert hast |
| **C — SQL-Dump** `.sql` | Alternative zu direktem Dateikopie; gut für Prüfung in Git-ignored `data/backups/` |

Ohne Login im **alten** Railway-Konto kann niemand remote auf das alte Volume zugreifen. Du musst dich dort einloggen und `mabai.db` herunterladen oder kopieren.

---

## Lokaler Status prüfen

```bash
python tools/db_migrate.py inspect
python tools/db_migrate.py inspect --db data/mabai.db
```

Das Tool prüft `PRAGMA integrity_check`, listet Tabellen mit Zeilenanzahl und zeigt bis zu 20 User.

**Hinweis:** Eine frisch initialisierte leere DB hat ~45 KiB und 0 Zeilen in `users` — das ist **kein** Production-Backup.

---

## Option A — Vom alten Railway-Volume (empfohlen)

### A1 — Datei aus altem Projekt holen

1. [railway.app](https://railway.app) mit dem **alten** Konto öffnen
2. Projekt mit `mabai-production.up.railway.app` → **Streamlit-Service** → **Volumes**
3. Volume ist auf `/data` gemountet; die Datei heißt `/data/mabai.db`

**Variante 1 — Railway CLI (One-Off Shell):**

```bash
railway login                    # altes Konto
railway link                     # altes Projekt + Streamlit-Service
railway run -- sh -c 'ls -la /data && cp /data/mabai.db /tmp/mabai.db && ls -la /tmp/mabai.db'
# Datei aus Container kopieren (Railway UI „Connect“ / volume export, je nach Plan)
```

**Variante 2 — One-Off mit Base64 (kleine DBs, &lt; ~10 MB):**

```bash
railway run -- sh -c 'base64 /data/mabai.db' > data/backups/mabai-from-old.b64
# Lokal dekodieren (PowerShell):
# [IO.File]::WriteAllBytes("data/backups/mabai.db", [Convert]::FromBase64String((Get-Content data/backups/mabai-from-old.b64 -Raw)))
```

**Variante 3 — Temporärer Download-Endpunkt** (nur wenn du einen sicheren Admin-Weg hast; nicht ins Repo committen).

### A2 — Ins neue Railway-Projekt legen

1. Mit **maksigewinnt@gmail.com** einloggen: `railway login`
2. Neues Projekt verlinken: `railway link` → Service mit Volume `/data`
3. **Vor dem Upload:** App stoppen oder keinen gleichzeitigen Schreibzugriff auf `/data/mabai.db`

**Upload per CLI (One-Off):**

Lokale Datei zuerst prüfen:

```bash
python tools/db_migrate.py verify --db data/backups/mabai-from-old.db
```

Dann ins neue Volume (Base64-Pipe — Beispiel; Größe beachten):

```bash
railway login                    # neues Konto
railway link                     # neues Projekt
# Backup lokal bereitstellen, dann im One-Off:
railway run -- sh -c 'cat > /data/mabai.db' < data/backups/mabai-from-old.db
```

Alternativ: Railway Dashboard → Volume → wenn „Download/Upload“ verfügbar, `mabai.db` nach `/data/mabai.db` legen.

### A3 — Umgebung im neuen Projekt

| Einstellung | Wert |
|-------------|------|
| Volume mount | `/data` |
| Variable | `DATA_DIR=/data` |
| Stripe-Webhook (optional) | **Gleiches** Volume + `DATA_DIR=/data` |

Redeploy → Login mit bestehendem User testen.

---

## Option B — Von lokaler Kopie

Wenn `data/mabai.db` echte User-Daten enthält:

```bash
python tools/db_migrate.py backup --out data/backups/mabai-$(date +%Y%m%d).db
python tools/db_migrate.py verify --db data/backups/mabai-YYYYMMDD.db
```

Upload wie in [Option A2](#a2--ins-neue-railway-projekt-legen).

Lokal wiederherstellen:

```bash
python tools/db_migrate.py restore --from data/backups/mabai-YYYYMMDD.db --force
```

---

## Option C — SQL-Export / -Import

Export (benötigt `sqlite3` CLI):

```bash
python tools/db_migrate.py export-sql --out data/backups/mabai-dump.sql
```

Import auf neuem Server (One-Off, **leere** oder ersetzte DB):

```bash
railway run -- sh -c 'rm -f /data/mabai.db && sqlite3 /data/mabai.db' < data/backups/mabai-dump.sql
```

Oder lokal:

```bash
sqlite3 data/mabai.db < data/backups/mabai-dump.sql
python tools/db_migrate.py inspect
```

---

## Tabellen in mabai.db (Schema-Referenz)

Kern (`db/core.py`): `users`, `football_daily_usage`, `support_tickets`, `support_ticket_replies`, `app_error_logs`, `usage_logs`, `redeem_codes`, `payments`, `login_logs`, `audit_logs`

Erweiterungen (`db/app.py`, `db/video_engine.py`): u. a. `automations`, `projects`, `leads`, `video_jobs`, `reels`, `social_connections`, …

Nach Restore: `ensure_db_ready()` in `main.py` führt idempotente `ALTER TABLE` aus — **kein** separates Migrations-Skript nötig.

---

## Sicherheit & Git

- **`data/` und `*.db` sind in `.gitignore`** — niemals `mabai.db` mit User-Daten committen
- Backups nur unter `data/backups/` (ebenfalls ignoriert)
- API-Keys bleiben in Railway Variables, nicht in der DB

---

## Verifikation nach Migration

```bash
# Lokal
python tools/db_migrate.py inspect --db data/backups/mabai-from-old.db

# Auf Railway (One-Off)
railway run -- python tools/db_migrate.py inspect
```

In der App:

1. Mit **bestehendem** User einloggen (nicht nur neu registrieren)
2. Admin: User-Anzahl, Tickets, Football-Nutzung prüfen
3. Stripe-Webhook-Service: gleiche DB → Zahlungen konsistent

Healthcheck:

```bash
curl -sS https://web-production-734b0.up.railway.app/_stcore/health
```

---

## Kurz-Checkliste

- [ ] Altes Railway-Konto: `mabai.db` von `/data` exportiert
- [ ] `python tools/db_migrate.py verify` — Integrität ok, User &gt; 0
- [ ] Neues Projekt: Volume `/data`, `DATA_DIR=/data`
- [ ] `mabai.db` nach `/data/mabai.db` kopiert (App kurz stoppen)
- [ ] Redeploy, Login-Test mit altem Account
- [ ] Optional: Stripe-Webhook-Service mit gleichem Volume
- [ ] Altes Projekt erst nach erfolgreichem Test abschalten

Siehe auch: [`docs/RAILWAY_MIGRATION.md`](RAILWAY_MIGRATION.md) (Projekt-Neuaufbau), [`docs/RAILWAY_DEPLOY.md`](RAILWAY_DEPLOY.md) (Volume-Setup).
