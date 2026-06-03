# MaByte — AI Handover

> **Single Source of Truth** · Max. 2 Seiten · Stand **2026-06-02** · Branch `main`  
> Vollständiger Kontext: [PROJECT_STATE.md](PROJECT_STATE.md)

---

## Was funktioniert

- **App-Start:** `main.py` → `ui.py`, DB via `database.ensure_db_ready()`.
- **Auth:** Login/Register (`pages/auth.py`), Google OAuth (wenn ENV gesetzt), Session (`services/session_auth.py`).
- **Navigation:** Eine Sidebar (`ui/sidebar.py`, 230px), Router in `ui.py` (`PAGE_HANDLERS`).
- **Dashboard:** `ui/dashboard.py` — Hero, Quick Actions, Tokens/Plan/Aktivität.
- **AI Chat:** OpenAI mit Token-Abzug (`pages/chat.py`).
- **Football AI:** `football_feed.py` — Topspiele strikt per Liga-ID; Alle Spiele Raw max 50; keine Fake-Tipps in der Liste.
- **Analyse:** On-demand `fetch_match_detail` — Odds, Predictions, Form, Injuries wenn API liefert.
- **Creator:** Image/Video/Music/Code über `pages/media.py` + Provider ENV.
- **Projects / Automations:** DB + Basis-UI (`projects.py`, `automation_lab.py`).
- **Profile / Premium:** Account + Stripe Checkout (`account.py`, `premium.py`).
- **Deploy:** Railway (`start.sh`, `railway.toml`), Webhook optional separat (`webhook_service.py`).

---

## Was kaputt / riskant ist

| Problem | Impact |
|---------|--------|
| **Kein `FOOTBALL_API_KEY` oder Free-Tier** | Topspiele leer → „Heute keine Topspiele verfügbar.“ |
| **Falsche `FOOTBALL_DEFAULT_SEASON`** | Liga-Fetch liefert 0 Fixtures |
| **API Rate Limit** | Warnungen, ggf. stale cache |
| **Analyse-Button selten aktiv** | Probes brauchen Odds/Predictions |
| **Streamlit Full Rerun** | Jede Sidebar-Navigation lädt Seite neu |
| **OAuth `invalid_request`** | Redirect-URI / Google Console / `APP_BASE_URL` falsch |
| **Multi-Instance Railway** | In-memory Rate-Limits nicht shared |
| **Media Import-Fehler** | `ui.py` zeigt Fehlerseite wenn `pages/media.py` bricht |

**Nicht im User-Frontend:** Admin-UI (`pages/admin.py` existiert nicht). Rollen/Admin nur in DB + `server_is_admin()` — kein separates Admin-Panel.

---

## Bekannte Bugs

1. Sidebar-Footer klebt nicht in allen Browsern perfekt unten (`:has(.sb-foot)`).
2. Header 64px vs Studios mit 92px `padding-top` (`pages/media.py`, `ui/video_engine_ui.py`).
3. `KNOWN_ISSUES.md` / `BETA_READINESS.md` teils veraltet (Admin-UI, Odds Lab).
4. Football: lokaler Smoke oft `displayed_topspiele_count=0` ohne Paid Key.
5. Stripe Yearly UI ohne echte Yearly Price IDs.

---

## Als Nächstes (siehe ROADMAP)

1. Railway ENV: `FOOTBALL_API_KEY`, `FOOTBALL_DEFAULT_SEASON`, `APP_BASE_URL`, `DATA_DIR`, `OAUTH_STATE_SECRET`.
2. Production-Smoke: Login → Dashboard → Football Topspiele → Alle Spiele.
3. Stripe Yearly + einheitliches Studio-Layout (64px).
4. E2E (Playwright) + Legal-Texte vor Marketing.

**Nicht ohne Auftrag:** Football-Filter lockern, neue Sidebar-Features, Admin-UI zurückbauen.

---

## Quick Reference

```
Einstieg:      main.py → ui.py
Sidebar:       ui/sidebar.py
Home:          ui/dashboard.py
Football UI:   ui/football.py
Football Feed: services/football_feed.py
Football API:  services/football_service.py
Config/ENV:    config.py, .env.example
DB:            database.py → db/*
Test:          python tools/test_football_feed.py
UI-Version:    ui/app_shell.py → _UI_VERSION = 16
```

**Topspiele-Ligen:** 78, 79, 81, 2, 3, 848, 39, 140, 135, 61

---

*Bei Konflikt: [PROJECT_STATE.md](PROJECT_STATE.md) + Git `main`.*
