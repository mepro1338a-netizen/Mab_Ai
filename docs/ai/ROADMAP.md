# MaByte — Roadmap

> **Single Source of Truth** · Stand **2026-06-02**  
> Strategie: **Beta stabilisieren** — keine neuen Features ohne expliziten Auftrag.

**Verwandt:** [TECH_DEBT_REPORT.md](TECH_DEBT_REPORT.md) · [PROJECT_STATE.md](PROJECT_STATE.md)

---

## Phase 0 — Jetzt (Production Beta)

**Ziel:** App auf Railway mit echten Football-Daten und korrekter Auth/Billing nutzbar.

| # | Task | Priorität | Status |
|---|------|-----------|--------|
| 0.1 | Railway ENV verifizieren (`FOOTBALL_API_KEY`, `FOOTBALL_DEFAULT_SEASON`, `APP_BASE_URL`, `DATA_DIR`, `OAUTH_STATE_SECRET`) | P0 | Offen |
| 0.2 | Production-Smoke: Login → Dashboard → Football Topspiele (Whitelist) → Alle Spiele (Banner) | P0 | Offen |
| 0.3 | Legal/Impressum mit echten Firmendaten | P0 | Offen |
| 0.4 | `docs/ai/*` nach größeren Änderungen aktualisieren | P2 | **Erledigt** (Initial 2026-06-02) |

---

## Phase 1 — Stabilisierung (nächster Sprint)

**Ziel:** UX-Konsistenz, Billing vollständig, Docs sync.

| # | Task | Priorität | Abhängigkeit |
|---|------|-----------|--------------|
| 1.1 | Stripe Yearly Price IDs + Checkout verdrahten | P1 | Stripe Dashboard |
| 1.2 | Einheitliches Topbar-Padding 64px auf allen Studios | P1 | `media.py`, `video_engine_ui.py` |
| 1.3 | `KNOWN_ISSUES.md` / `BETA_READINESS.md` an `docs/ai` anpassen | P2 | — |
| 1.4 | Sidebar Footer ohne `:has()` Fallback | P3 | `ui/sidebar.py` |
| 1.5 | Playwright E2E: Auth → Dashboard → Football → Premium | P2 | CI optional |

---

## Phase 2 — Skalierung & Ops

**Ziel:** Multi-Instance-tauglich, bessere Observability.

| # | Task | Priorität |
|---|------|-----------|
| 2.1 | Redis (oder DB) für Rate-Limits | P2 |
| 2.2 | `@st.cache_data` für teure Football-Payloads (user-scoped) | P2 |
| 2.3 | `static/og-preview.png` für SEO/Social | P3 |
| 2.4 | Optional: Admin-Read-Only UI **oder** BETA-Doc korrigieren (kein Admin-Panel heute) | P2 |

---

## Phase 3 — Refactoring (kein Feature-Sprint)

**Ziel:** Wartbarkeit ohne Verhaltensänderung.

| # | Task | Dateien |
|---|------|---------|
| 3.1 | `pages/media.py` in Studio-Module splitten | `pages/media.py` |
| 3.2 | `football_board.py` verkleinern (nur Detail/Odds) | `services/football_*` |
| 3.3 | `db/app.py` nach Domänen trennen | `db/` |
| 3.4 | Legacy Shims entfernen wenn Imports bereinigt | **Erledigt** 2026-06-03 (`ai_dashboard`, `football_betting_board`, `football_logic`) |
| 3.5 | Global Cleanup: ungenutzte tools/tests | **Erledigt** — siehe [CLEANUP_REPORT.md](CLEANUP_REPORT.md) |

---

## Explizit nicht geplant (ohne User-Auftrag)

- Football-Whitelist lockern oder Raw in Topspiele
- Neue Sidebar-Menüpunkte / Navigation umbauen
- Admin Command Center zurückbauen
- Neue Creator-Provider
- Migration weg von Streamlit

---

## Meilensteine

| Meilenstein | Kriterium | Ziel-Datum |
|-------------|-----------|------------|
| **Beta Live** | Railway + Paid Football + Login/OAuth | Offen |
| **Billing Complete** | Monthly + Yearly Stripe | Phase 1 |
| **Ops Ready** | E2E Smoke grün, Legal live | Phase 1–2 |
| **Maintainability** | media.py split, shims weg | Phase 3 |

---

## Changelog (Roadmap)

| Datum | Änderung |
|-------|----------|
| 2026-06-02 | Initial aus PROJECT_STATE TODO + BETA_READINESS + Conversation Rebuild |

---

*Nach jedem größeren Merge: relevante Phase-Tasks auf „Erledigt“ setzen, neue Items unten anfügen.*
