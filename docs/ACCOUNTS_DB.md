# Accounts-Datenbank — was gespeichert wird & wie sie dauerhaft bleibt

MaByte hat **bereits** eine Datenbank, die **alle Accounts** speichert. Es muss
keine neue DB gebaut werden. Der einzige kritische Punkt ist die **Persistenz auf
Railway** (Volume) — ohne Volume gehen die Accounts bei jedem Redeploy verloren.

---

## Symptom: "die Datenbank greift nicht" / Accounts nach Deploy weg

> **Ursache in 99 % der Fälle:** In Railway ist **kein Volume auf `/data`**
> gemountet. Die App schreibt dann in das Container-Dateisystem (`<repo>/data`),
> das bei jedem Redeploy gelöscht wird.

**In 60 Sekunden prüfen:**

1. Railway → Service (Streamlit) → **Deployments** → letzte Logs öffnen. Beim
   Boot loggt MaByte jetzt eine Zeile wie:
   ```
   DB boot: DATA_DIR=/data DB_PATH=/data/mabai.db env_DATA_DIR=/data
   railway=True db_exists=True db_size=... users_before_init=... writable=True
   ```
   Wenn `DATA_DIR` nicht `/data` ist **oder** `writable=False` erscheint **oder**
   die Warnung `Railway erkannt, aber DATA_DIR liegt NICHT auf /data` auftaucht →
   siehe Fix in Abschnitt 3.

2. Alternativ als One-off im Railway-Service:
   ```bash
   railway run python tools/db_status.py
   ```
   Zeigt DATA_DIR, DB-Pfad, Größe, User-Anzahl und einen Volume-Check.

**Fix (immer derselbe):** siehe [Abschnitt 3 — Persistenz garantieren](#3-persistenz-garantieren-railway--die-wichtigen-schritte).

---

## 1. Was existiert bereits

- **Engine:** SQLite, eine einzige Datei `{DATA_DIR}/mabai.db` (`config.py` → `DB_PATH`).
- **Kein PostgreSQL** — es gibt keine `DATABASE_URL`. SQLite + Volume ist das
  gewollte Design.
- **Tabelle `users`** (`db/core.py`, `init_db()`) speichert jeden Account:

| Spalte | Inhalt |
|--------|--------|
| `id` | Auto-ID |
| `username` | eindeutiger Benutzername (kleingeschrieben) |
| `email` | eindeutige E-Mail |
| `password_hash` | **bcrypt**-Hash (nie Klartext) |
| `plan` | `free` / `pro` / `grand` / `elite` |
| `tokens` | Guthaben |
| `role`, `admin_level` | Rolle & Rechte (`user` … `owner`/1337) |
| `is_banned` | Sperrflag |
| `automation_unlocked` | Auto-Posting freigeschaltet |
| `football_plan` | Football-Abo (`none` … `football_elite`) |
| `oauth_provider`, `oauth_sub` | Google/OAuth-Login |
| `display_name`, `company`, `phone`, `country`, `use_case`, `marketing_opt_in` | Profil-/CRM-Felder |
| `created_at`, `last_login` | Zeitstempel |

- **Registrierung/Login:** `db/users.py` (`register_account`, `verify_login`,
  `oauth_login_or_register`). Jede Registrierung legt zusätzlich einen `leads`-Eintrag an.
- **Init:** `ensure_db_ready()` (`database.py`) ruft `init_db()` + `force_owner_account()`
  idempotent bei jedem Start auf — inklusive `ALTER TABLE` für neue Spalten.

Die Accounts werden also **schon jetzt vollständig gespeichert** — dauerhaft ist es
aber nur mit dem richtigen Speicherort (siehe unten).

---

## 2. Speichert die aktuelle Konfiguration dauerhaft?

`config.py` wählt `DATA_DIR` so:

```python
DATA_DIR = Path(os.getenv("DATA_DIR", "/data" if Path("/data").exists() else BASE_DIR / "data"))
```

| Situation | Ergebnis |
|-----------|----------|
| `DATA_DIR=/data` **und** Volume auf `/data` gemountet | **Dauerhaft** — Accounts überleben Redeploys ✅ |
| Kein Volume (DB liegt im Container-Dateisystem) | **Flüchtig** — jeder Redeploy/Neustart löscht alle Accounts ❌ |

Ein Railway-Volume steht **nicht** in `railway.toml` — es wird nur im Dashboard
konfiguriert. Deshalb muss man dort prüfen, ob wirklich ein Volume auf `/data` liegt.

---

## 3. Persistenz garantieren (Railway) — die wichtigen Schritte

1. Railway → Projekt → **Streamlit-Service** → **Variables**
   - `DATA_DIR=/data`
2. Gleicher Service → **Volumes** → **New Volume**
   - Mount Path: `/data`
3. Falls ein separater **Stripe-Webhook-Service** existiert:
   - **dasselbe** Volume auch dort auf `/data` mounten und `DATA_DIR=/data` setzen,
     damit beide Services dieselbe `mabai.db` teilen.
4. **Redeploy**, danach mit einem bestehenden Account einloggen und einen Redeploy
   testen — der Account muss erhalten bleiben.

> Ohne Schritt 1 + 2 gehen bei jedem Deploy **alle** Accounts verloren.

---

## 4. Accounts prüfen / exportieren

Anzahl und Liste aller Accounts (ohne Passwörter):

```bash
python tools/list_accounts.py            # DB-Pfad + Anzahl + alle Accounts
python tools/list_accounts.py --count    # nur die Anzahl
python tools/list_accounts.py --csv data/backups/accounts.csv
railway run python tools/list_accounts.py   # direkt auf dem Railway-Volume
```

DB-Gesamtüberblick (Integrität, alle Tabellen, Zeilen):

```bash
python tools/db_migrate.py inspect
railway run python tools/db_migrate.py inspect
```

Persistenz-Check (kurz, mit Volume-Erkennung):

```bash
python tools/db_status.py            # DATA_DIR, DB, Größe, User-Anzahl, Volume-Check
railway run python tools/db_status.py
```

Im Admin-Panel (`pages/admin.py`) gibt es zusätzlich einen **User-Export als CSV**.

---

## 5. Backups

```bash
python tools/db_migrate.py backup       # Kopie nach data/backups/
python tools/db_migrate.py export-sql   # SQL-Dump (braucht sqlite3 CLI)
```

Migration zwischen Railway-Konten: siehe [`docs/DATABASE_MIGRATION.md`](DATABASE_MIGRATION.md).

---

## 6. Sicherheit

- `data/` und `*.db` sind in `.gitignore` — **nie** eine DB mit echten Accounts committen.
- Passwörter liegen ausschließlich als bcrypt-Hash vor.
- API-Keys gehören in Railway-Variables, nicht in die DB.
