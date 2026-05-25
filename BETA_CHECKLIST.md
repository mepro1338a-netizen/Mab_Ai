# MaByte Production Beta Checklist

## UX / Design System
- [x] Globales Designsystem (`ui/design_system.py`) in `load_css()`
- [x] Dark-SaaS Buttons, Formulare, Tabellen, Mobile Breakpoints
- [x] OS Guide in Sidebar (`ui/os_helper.py`)
- [ ] Alle Seiten manuell auf Mobile (iPhone/Android) durchklicken
- [ ] Mojibake-Audit in `pages/*.py` (UTF-8 speichern)

## Core Flows
- [ ] Login / Register / Logout
- [ ] Google OAuth (Redirect exakt in Console)
- [ ] Stripe Checkout Pro / Grand / Elite
- [ ] Stripe Football Starter / Pro / Elite
- [ ] Redeem Codes
- [ ] Support Ticket + Admin Antwort

## Football Premium
- [x] Elite Odds Lab: EV, Confidence, Bankroll-Hinweis
- [ ] Starter: limitierte Tabs sichtbar, Upgrade-Cards
- [ ] Pro: Predictions + H2H
- [ ] API-Fallback wenn `FOOTBALL_API_KEY` fehlt

## Stability
- [x] `safe_render()` Error Boundary in `ui.py`
- [x] DB `ensure_db_ready()` ohne Import-Crash
- [ ] Healthcheck Railway `/_stcore/health`

## Security
- [ ] Admin Panel nur mit Rolle
- [ ] OAuth State Secret gesetzt (`OAUTH_STATE_SECRET`)
- [ ] Keine Secrets in Git / Logs

## Performance
- [x] Football API Memory+Disk Cache (bestehend)
- [ ] Schwere Football-Tabs lazy (Session-State)

## Deploy
- [ ] `APP_BASE_URL=https://mabyte.de`
- [ ] `DATA_DIR=/data` Volume
- [ ] Env laut `ENV_SETUP.md`

## Sign-off
- [ ] Owner: mepro1337 — Beta Go/No-Go
- [ ] Support-Inbox getestet
- [ ] Known Issues reviewed
