# Known Issues — MaByte Beta

## UI
- **Doppeltes CSS**: Einige Seiten injizieren zusätzlich eigenes CSS (`football`, `admin`, `account`) — kann zu leichten Abweichungen führen.
- **Jährliche Abrechnung**: Toggle auf Premium vorbereitet; Stripe Yearly Prices noch nicht verdrahtet.
- **Streamlit Reruns**: Jede Sidebar-Navigation triggert Full Rerun — erwartetes Streamlit-Verhalten.

## Football
- **API-Football Limits**: Ohne `FOOTBALL_API_KEY` zeigen Live-Tabs Fallback-Meldungen (kein Crash).
- **Odds Lab**: Mathematische Analyse only — keine Wettberatung.

## Auth
- **Google OAuth**: `invalid_request` wenn Redirect-URI oder Test-User in Console fehlen — siehe `docs/GOOGLE_OAUTH_SETUP.md`.
- **Kein Auto-Linking**: Gleiche E-Mail mit Passwort-Account blockiert OAuth-Link bis Passwort-Login.

## Support
- **Neue Tabelle**: `support_ticket_replies` wird bei `init_db()` angelegt — bestehende DBs migrieren automatisch via `CREATE IF NOT EXISTS`.

## Media
- **Import-Fehler**: `pages/media.py` Import-Fehler werden in `ui.py` abgefangen und als Fehlerseite gezeigt.

## Empfohlene Fixes (nächster Sprint)
1. Stripe Yearly Price IDs + Checkout-Parameter
2. Einheitliche `premium_foundation_css()` auf allen Account-Seiten
3. `@st.cache_data` für teure Football-Listen (Ligen/Fixtures)
4. E2E-Smoke-Tests (Playwright) für Auth + Premium
