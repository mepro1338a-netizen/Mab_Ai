# MaByte — Technical Debt Report

> **Single Source of Truth** · Stand **2026-06-02**  
> Beta-Score: **78/100** (`BETA_READINESS.md`) · Ergänzt [PROJECT_STATE.md](PROJECT_STATE.md)

**Pflege-Regel:** Nur neue/behobene Punkte eintragen; erledigte Items nach „Erledigt“ verschieben, nicht löschen ohne Kontext.

---

## Legende

| Severity | Bedeutung |
|----------|-----------|
| **P0** | Blockiert Production-Nutzen oder Compliance |
| **P1** | Deutliche UX/Qualitäts-Einbuße |
| **P2** | Wartbarkeit, Skalierung, Tech-Hygiene |
| **P3** | Nice-to-have |

---

## Offen

### P0 — Critical

| ID | Thema | Beschreibung | Betroffene Dateien |
|----|-------|--------------|-------------------|
| TD-001 | Football API Production | Ohne Paid `FOOTBALL_API_KEY` + korrekte `FOOTBALL_DEFAULT_SEASON` → 0 Topspiele | `config.py`, `football_service.py`, Railway ENV |
| TD-002 | Legal / Impressum | Platzhalter vor öffentlichem Marketing (`BETA_READINESS`) | Legal-Pages in `ui.py` / Account |
| TD-003 | `OAUTH_STATE_SECRET` | Dev-Fallback unsicher in Production | `oauth_service.py`, Railway ENV |

### P1 — High

| ID | Thema | Beschreibung | Betroffene Dateien |
|----|-------|--------------|-------------------|
| TD-010 | Streamlit Full Rerun | Jede Navigation = kompletter Rerun; langsam wahrgenommen | Gesamt-App |
| TD-011 | Layout-Inkonsistenz | Global 64px Header, Studios 92px `padding-top` | `pages/media.py`, `ui/video_engine_ui.py` |
| TD-012 | Stripe Yearly | UI-Toggle ohne vollständige `STRIPE_PRICE_*` Yearly IDs | `pages/premium.py`, `payments.py` |
| TD-013 | Football Analyse-Probes | Bis 10 zusätzliche API-Calls pro Topspiele-View | `ui/football.py`, `football_board.py` |
| TD-014 | Veraltete Root-Docs | `KNOWN_ISSUES.md`, `PROJECT_STRUCTURE.md`, `BETA_READINESS.md` erwähnen Admin-UI / alte Pfade | Root `*.md` |
| TD-015 | Sidebar Footer | `margin-top: auto` via `:has(.sb-foot)` — browserabhängig | `ui/sidebar.py` |

### P2 — Medium

| ID | Thema | Beschreibung | Betroffene Dateien |
|----|-------|--------------|-------------------|
| TD-020 | In-memory Rate Limits | Nicht shared bei Multi-Instance Railway | `security.py` |
| TD-021 | Session-Modell | Kein HttpOnly-Cookie; Streamlit `session_state` | `services/session_auth.py` |
| TD-022 | `pages/media.py` Größe | ~1200+ Zeilen, schwer wartbar | `pages/media.py` |
| TD-023 | `db/app.py` Größe | Monolith — Domänen-Trennung offen | `db/app.py` |
| TD-024 | Legacy Shims | Doppelte Import-Pfade | `ai_dashboard.py`, `football_*` shims |
| TD-025 | Kein E2E | Nur `tools/test_football_feed.py` Smoke | `tools/` |
| TD-026 | SEO OG Image | `static/og-preview.png` fehlt / Platzhalter | `ui.py` SEO-Injection |
| TD-027 | `football_loaders` | `fetch_premium_dashboard` noch komplex; Teil-Overlap mit `football_feed` | `football_loaders.py` |
| TD-028 | Admin ohne UI | `admin_level`/Rollen in DB, kein `pages/admin.py` — Ops nur DB/Logs | `db/users.py`, `BETA_READINESS` (irreführend) |

### P3 — Low

| ID | Thema | Beschreibung |
|----|-------|--------------|
| TD-030 | CDN für Assets | Bilder lokal im Repo |
| TD-031 | `@st.cache_data` Football | User-scoped Cache noch nicht einheitlich |
| TD-032 | Globales Button-CSS vs Sidebar | Seltene Konflikte `app_shell` vs Sidebar | `ui/app_shell.py` |
| TD-033 | Ungenutzte tools/tests | Aufräumen nach Refactor (Phase 4 Cleanup offen) | `tools/` |

---

## Erledigt (Referenz)

| ID | Thema | Erledigt ca. |
|----|-------|--------------|
| TD-DONE-01 | Doppelte Sidebar (`sidebar_nav.py`) | Juni 2026 → `ui/sidebar.py` |
| TD-DONE-02 | Topspiele Raw-Fallback / Curated-Dump | `ff0a920` — `football_feed.py` strict |
| TD-DONE-03 | Fake KI-Tipps / Debug-Stats Football UI | `ui/football.py` rebuild |
| TD-DONE-04 | Date-Scan aller Ligen in `get_premium_fixtures_upcoming` | Liga-ID-only v4 cache |
| TD-DONE-05 | Großes Slogan-Banner Header | 64px `ui/header.py` |
| TD-DONE-06 | Überladenes Home Command Center | `ui/dashboard.py` minimal |
| TD-DONE-07 | Doppelte Sidebar-CSS in `app_shell` | Sidebar owned by `sidebar.py` |
| TD-DONE-08 | `psycopg2` in requirements | Entfernt (unused) |

---

## Dokumentations-Schulden

| Datei | Problem | Maßnahme |
|-------|---------|----------|
| `KNOWN_ISSUES.md` | Admin, Odds Lab, doppeltes CSS veraltet | Mit diesem Report sync oder auf `docs/ai/` verweisen |
| `BETA_READINESS.md` | „Admin / Ops 85%“ — kein Admin-Frontend | Score-Kommentar anpassen |
| `PROJECT_STRUCTURE.md` | Alte Pfade | Deprecate → `docs/ai/PROJECT_STATE.md` |
| Root `PROJECT_STATE.md` | Duplikat | Zeigt auf `docs/ai/` |

---

## Metriken (Trend)

| Metrik | Wert | Ziel |
|--------|------|------|
| Python LOC | ~17.4k | stabil / sinken durch Split media |
| Test-Automatisierung | 1 Smoke-Script | + Playwright E2E |
| UI-Version | 16 | bump nach CSS-Deploy |

---

*Neue Schulden: hier eintragen mit nächster freier TD-XXX-ID. Behobene: nach „Erledigt“ mit Datum.*
