# MaByte — Project Stabilization Audit (Beta)

**Date:** 2026-06-03  
**Scope:** Football AI · Content Automation · Dashboard · Sidebar  
**Rule:** No new pages, modules, or APIs — stabilization only.

---

## Executive summary

MaByte is close to a **stable beta** (~78/100 per `BETA_READINESS.md`). The four focus areas have clear UI shells; the main risks are **deploy drift** (Football V2 not on `origin/main`), **Content Automation marketing vs. reality**, and **production env** (API keys, OAuth secrets). This document is the beta stabilization SSOT.

---

## 1. Completed features

### Sidebar
- [x] Grouped SaaS navigation (Workspace, Football, Creator Studio, Content Automation, Account)
- [x] Inline SVG icons via HTML `?nav=` links
- [x] Scrollable `.sb-scroll` shell + fixed footer (user + logout)
- [x] Legacy aliases (`projects` → home, `automations` → automation_lab)
- [x] Single source: `ui/sidebar.py`

### Dashboard (home)
- [x] Card-based workspace home (`ui/dashboard.py`)
- [x] Stats row (Tokens, Plan, Activity)
- [x] Module tiles with `?nav=` deep links
- [x] Account shortcuts (Profile, Elite)
- [x] No Football quick-action dominance (removed from hero)

### Global chrome
- [x] Fixed topbar (`ui/chrome.py`) with page badge
- [x] `apply_nav_from_query()` for sidebar + dashboard links
- [x] Error boundary in `ui.py` (`safe_render`)

### Football AI (local — see Broken)
- [x] V2 UI package: `ui/football/` (page, cards, analysis, nav constants)
- [x] Service layer unchanged: `football_service`, `football_feed`, `football_board`, cache, DB
- [x] Top nav: Deutschland / UEFA / Topligen / Nationalteams
- [x] Time filter: Heute / Live / Morgen / Nächste
- [x] League sub-filters per competition
- [x] Match cards + on-demand `fetch_match_detail`
- [x] Analysis panel with real-data gate + German “no data” message
- [x] `tools/test_football_feed.py` whitelist smoke (passes locally)

### Content Automation
- [x] SaaS page layout (`pages/automation_lab.py`)
- [x] Platform cards (Instagram, TikTok, YouTube Shorts)
- [x] Active automations table (legacy agent rows filtered out)
- [x] Create form → `create_automation()` in SQLite
- [x] Route + sidebar label “Content Automation”

### Profile (related to dashboard cleanup)
- [x] OS Guide removed
- [x] Payments table UI (`render_payments` in `ui/components.py`)
- [x] Activity + limits sections

### Infra (unchanged, still valid)
- [x] Auth + session rotation (`services/session_auth.py`)
- [x] Stripe checkout + webhook service
- [x] Football API client + disk/memory cache
- [x] Premium / football plan gating

---

## 2. Unfinished features

### Football AI
- [ ] **Deploy V2** — `ui/football/` exists locally; `origin/main` still has monolithic `ui/football.py` (see Broken)
- [ ] Analysis probe only first **10** fixtures per load (`enrich_rows_analysis_flags` max_probe) — rest show “Analyse nicht verfügbar” without click-test
- [ ] Full analysis (injuries, H2H, predictions) requires **football_pro+** plan rank — Starter users see limited detail by design (needs clear UI copy)
- [ ] No loading skeleton / retry UX on API rate-limit errors
- [ ] Docs (`docs/ai/PROJECT_STATE.md`) still describe old football file layout

### Content Automation
- [ ] **No job runner** — `create_automation` writes DB only; `automation_runs` table never populated from UI
- [ ] Card bullets promise “Generate Content / Schedule Post / Auto Publish” but only **pre-fills form** — no publish pipeline wired on this page
- [ ] No OAuth status (“Connect Instagram”) on Content Automation page
- [ ] `services/social_publish.py` exists for **video jobs**, not linked to `automation_lab` automations
- [ ] Mixed EN/DE labels (Platform, Daily, Active)
- [ ] Status column always “active” — no pause/edit/delete

### Dashboard
- [ ] Emoji module icons (not Lucide — inconsistent with sidebar)
- [ ] `?nav=` causes full reload (Streamlit limitation — acceptable but not SPA-smooth)
- [ ] Profile page reuses `.mb-dash` CSS scope — minor style bleed risk with home dashboard

### Sidebar
- [ ] `?nav=` full page reload (expected; document for QA)
- [ ] Very small viewports: logout button can sit below fold if shell height miscalc (rare)

---

## 3. Broken / at-risk features

| Item | Severity | Evidence |
|------|----------|----------|
| **Football V2 not on production branch** | **Critical** | `git status`: `?? ui/football/`, `D ui/football.py`, uncommitted `ui.py` session defaults `fb_v=10` |
| **Empty Football lists without API key** | High | `tools/test_football_feed.py` → 0 rows, banner “Nächste Spiele”; looks broken to users |
| **Content Automation “automation” does nothing after save** | High | No worker/cron; misleading product promise |
| **Dead code: `pages/projects.py`** | Low | Routed away (`projects` → home) but file remains — confuses audits |
| **Outdated SSOT docs** | Medium | `PROJECT_STATE.md` lists `ui/football.py`, Projects page, OS Guide |
| **BETA_CHECKLIST references removed modules** | Low | `ui/design_system.py`, `ui/os_helper.py` — files don’t exist |

---

## 4. High priority fixes (stabilization only)

1. **Ship Football V2** — commit + push `ui/football/` package; remove old `ui/football.py`; verify Railway import `from ui.football import …`
2. **Verify `FOOTBALL_API_KEY` on Railway** — without it, Football AI appears empty (not a code bug)
3. **Content Automation honesty** — change copy to “Automation speichern” / “Bald: Auto-Posting”; remove or disable false feature bullets until runner exists
4. **Smoke test after deploy** — login → Football → each top tab → one Analyse click; Content Automation create row; sidebar scroll to bottom
5. **Update `docs/ai/PROJECT_STATE.md`** — football package path, remove Projects/OS Guide from active nav

---

## 5. Roadmap

### Critical (before beta sign-off)

| # | Task | Area |
|---|------|------|
| C1 | Commit & deploy Football V2 UI package | Football |
| C2 | Confirm production env: `FOOTBALL_API_KEY`, `OAUTH_STATE_SECRET`, `DATA_DIR`, `APP_BASE_URL` | Infra |
| C3 | Content Automation: UI text matches actual behavior (save config only, no fake publish) | Content Automation |
| C4 | Manual QA script: auth, sidebar scroll, all nav links, football one analysis, automation create | All |
| C5 | Fix `PROJECT_STATE.md` + `AI_HANDOVER.md` to match live routes | Docs |

### Important (first beta patch, no new modules)

| # | Task | Area |
|---|------|------|
| I1 | Football: show clear banner when API key missing / quota exceeded | Football |
| I2 | Football: increase or remove `max_probe=10` cap OR show “Analyse prüfen” consistently | Football |
| I3 | Football: plan-tier hint on analysis view (Starter vs Pro) | Football |
| I4 | Content Automation: DE labels, status from DB, empty-state CTA to Elite/social connect | Content Automation |
| I5 | Dashboard: replace emoji with SVG or text-only for visual parity with sidebar | Dashboard |
| I6 | Profile: separate CSS marker `.mb-profile` vs `.mb-dash` | Dashboard |
| I7 | Sidebar: QA mobile + narrow height; tune `calc(100dvh - …)` if logout clipped | Sidebar |

### Optional (post-beta)

| # | Task | Area |
|---|------|------|
| O1 | Archive or delete `pages/projects.py` | Cleanup |
| O2 | Align `BETA_CHECKLIST.md` with current file tree | Docs |
| O3 | `@st.cache_data` on football competition fetch (session-keyed) | Performance |
| O4 | Playwright smoke: login + football + content automation | QA |
| O5 | Wire minimal automation runner (existing DB only — **new behavior**, defer if strict “no features”) | Content Automation |

---

## 6. Architecture snapshot (focus areas)

```
ui.py
├── render_sidebar()          → ui/sidebar.py
├── render_app_header()       → ui/chrome.py
├── render_home()             → ui/dashboard.py
├── render_football()         → ui/football/page.py
└── render_automation_lab()   → pages/automation_lab.py

services/ (unchanged)
├── football_service.py   # API + cache
├── football_feed.py      # competition feed
└── football_board.py     # detail + eligibility

pages/account.py          # Profile (limits, payments, activity)
```

---

## 7. Beta release definition of done

- [ ] All **Critical** items closed
- [ ] No P0 crashes on login → navigate all sidebar entries
- [ ] Football shows matches **with** valid API key on production
- [ ] Content Automation does not claim live posting unless implemented
- [ ] `KNOWN_ISSUES.md` reviewed and dated
- [ ] Owner sign-off on `BETA_CHECKLIST.md`

---

*Next update: after C1 deploy + C4 QA run.*
