# MaByte — Architecture Decisions (ADR)

> **Single Source of Truth** · Stand **2026-06-02**  
> Format: Kontext → Entscheidung → Konsequenzen. Neue ADRs unten anfügen, **nicht** alte löschen.

---

## ADR-001 — Streamlit als einziges Frontend

| | |
|---|---|
| **Status** | Akzeptiert |
| **Kontext** | Schneller SaaS-Prototyp, ein Python-Stack, kein separates React-Team |
| **Entscheidung** | Gesamte UI in Streamlit (`ui.py` + `pages/` + `ui/*`); CSS/HTML via `st.markdown` |
| **Konsequenzen** | Full Rerun pro Navigation; kein SPA; CSS in Python-Strings schwer zu testen |

---

## ADR-002 — SQLite auf Railway Volume

| | |
|---|---|
| **Status** | Akzeptiert |
| **Kontext** | Einfaches Deployment, geringe Ops-Komplexität |
| **Entscheidung** | `DATA_DIR/mabai.db`, Init in `db/core.py`, Facade `database.py` |
| **Konsequenzen** | Horizontale Skalierung der App-Instanzen braucht geteiltes Volume oder spätere Migration; Webhook-Service muss gleiches `DATA_DIR` nutzen |

---

## ADR-003 — Ein Router (`ui.py`), keine Streamlit-Multi-Page-App

| | |
|---|---|
| **Status** | Akzeptiert |
| **Kontext** | Konsistente Auth, SEO, Sidebar, Aliase |
| **Entscheidung** | `st.session_state.page` + `PAGE_HANDLERS`; `.streamlit/config.toml` → `showSidebarNavigation = false` |
| **Konsequenzen** | Eigene Sidebar Pflicht (`ui/sidebar.py`); keine `pages/` Auto-Discovery durch Streamlit |

---

## ADR-004 — Eine Sidebar-Komponente

| | |
|---|---|
| **Status** | Akzeptiert (Juni 2026 Rebuild) |
| **Kontext** | Mehrfache Sidebar-Implementierungen, CSS-Konflikte |
| **Entscheidung** | Nur `ui/sidebar.py` (230px, Lucide, flat nav); `sidebar_nav.py` entfernt |
| **Konsequenzen** | UI-Änderungen nur dort; `LEGACY_PAGE_ALIASES` für alte `page`-Keys |

---

## ADR-005 — Football Topspiele: strikte Liga-Whitelist

| | |
|---|---|
| **Status** | Akzeptiert (`ff0a920`) |
| **Kontext** | Topspiele zeigten untergeordnete/Raw-Ligen; Vertrauensverlust |
| **Entscheidung** | `FOOTBALL_TOPSPIELE_LEAGUE_IDS` in `config.py`; Auflösung nur in `football_feed.resolve_topspiele_board`; **kein** Raw-Fallback |
| **Konsequenzen** | Leere Liste bei fehlendem API-Key erwartet; „Alle Spiele“ separater Tab (max 50 Raw) |

---

## ADR-006 — Football-Analyse: keine Fake-Daten in der Liste

| | |
|---|---|
| **Status** | Akzeptiert |
| **Kontext** | Buttons aktiv ohne Odds/Predictions |
| **Entscheidung** | `probe_analysis_available` vor Button; Detail on-demand via `fetch_match_detail` |
| **Konsequenzen** | Zusätzliche API-Calls (Probes); Button oft deaktiviert ohne Paid API |

---

## ADR-007 — Schicht `football_feed` zwischen UI und Loader

| | |
|---|---|
| **Status** | Akzeptiert |
| **Kontext** | Logik verstreut in `football_logic`, `football_betting_board`, Loader |
| **Entscheidung** | `services/football_feed.py` als Feed-Single-Entry; Shims für alte Imports |
| **Konsequenzen** | Drei Schichten (feed → loaders → service); Shims später entfernen (Phase 3) |

---

## ADR-008 — Stripe Webhook als separater Prozess

| | |
|---|---|
| **Status** | Akzeptiert |
| **Kontext** | Streamlit nicht ideal für Webhook-POST |
| **Entscheidung** | `webhook_service.py` (aiohttp) als eigener Railway-Service |
| **Konsequenzen** | Zwei Services, gemeinsames `DATA_DIR`; keine Webhooks in `main.py` |

---

## ADR-009 — Session in Streamlit State + DB-Revalidation

| | |
|---|---|
| **Status** | Akzeptiert |
| **Kontext** | Kein klassisches Cookie-Session-Framework in Streamlit |
| **Entscheidung** | `session_token` in `st.session_state`; `enforce_active_session()` pro Request |
| **Konsequenzen** | Siehe TD-021; Rotation bei Login in `session_auth.py` |

---

## ADR-010 — Kein Admin-Frontend im Repo

| | |
|---|---|
| **Status** | Akzeptiert (aktuell) |
| **Kontext** | `pages/admin.py` nie shipped / entfernt; Rollen weiter in DB |
| **Entscheidung** | User-App ohne Admin-Panel; `server_is_admin()` für eingeschränkte Checks falls nötig |
| **Konsequenzen** | Ops über DB/Logs; `BETA_READINESS` Admin-Score irreführend — korrigieren in Phase 1 |

---

## ADR-011 — UI-Cache-Bust via `_UI_VERSION`

| | |
|---|---|
| **Status** | Akzeptiert |
| **Kontext** | Streamlit/CSS-Caching nach Deploy |
| **Entscheidung** | `ui/app_shell.py` → `_UI_VERSION` (aktuell **16**) in injiziertem CSS-Kommentar |
| **Konsequenzen** | Nach CSS-Änderung Version erhöhen + Hard-Refresh kommunizieren |

---

## ADR-012 — `docs/ai/` als AI Single Source of Truth

| | |
|---|---|
| **Status** | Akzeptiert (2026-06-02) |
| **Kontext** | Root-Docs (`PROJECT_STATE.md`) und verstreute MDs widersprüchlich |
| **Entscheidung** | Sechs Dateien unter `docs/ai/`; Root-Dateien nur Redirect; **aktualisieren statt neu erstellen** |
| **Konsequenzen** | Nach größeren Änderungen gezielt patchen; operative Docs (`docs/RAILWAY_DEPLOY.md`) bleiben parallel |

---

## Zurückgestellt / Abgelehnt

| Thema | Grund |
|-------|--------|
| Topspiele mit Curated/Raw-Fallback | Verwässert Produktversprechen — verworfen Juni 2026 |
| Date-Scan aller Ligen für Upcoming | API-Kosten + Noise — ersetzt durch Liga-ID-Fetch |
| PostgreSQL | Nicht benötigt für Beta; `psycopg2` aus requirements entfernt |

---

## ADR-Vorlage (kopieren für neue Entscheidungen)

```markdown
## ADR-XXX — Titel

| | |
|---|---|
| **Status** | Vorgeschlagen / Akzeptiert / Ersetzt durch ADR-YYY |
| **Datum** | YYYY-MM-DD |
| **Kontext** | … |
| **Entscheidung** | … |
| **Konsequenzen** | … |
```

---

*Ersetzte ADRs: Status auf „Ersetzt“ setzen und Verweis auf neue ADR-Nummer.*
