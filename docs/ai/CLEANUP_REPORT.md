# MaByte — Cleanup & Smoke Report

> **Stand:** 2026-06-03 · Branch `main`  
> Abschluss Phase 4 Rebuild + Global Cleanup

---

## Messung (vorher → nachher)

| Metrik | Vor Rebuild (Juni 2026) | Nach Cleanup |
|--------|-------------------------|--------------|
| Python-Dateien | ~59 | **58** (−3 Shims) |
| Python-Zeilen | ~17.389 | **~17.698** |
| UI-Module (`ui/` + `ui.py`) | 16 | **15** |
| Service-Module | 15 | **14** |
| Test-Tools (`tools/`) | 1 | **3** |
| Legacy Shims | 4 | **1** (`football_api.py` only) |

---

## Global Cleanup (erledigt)

### Entfernt — ungenutzte Shims (keine Imports im Repo)

| Datei | Grund |
|-------|--------|
| `ui/ai_dashboard.py` | Shim → `ui/dashboard.py`; nirgends importiert |
| `ui/football_betting_board.py` | Shim → `ui/football.py`; `ui.py` importiert direkt |
| `services/football_logic.py` | Shim → `football_feed`; nirgends importiert |

### Requirements geprüft

| Paket | Status |
|-------|--------|
| `streamlit-autorefresh` | **Entfernt** — nirgends importiert |
| `aiohttp`, `streamlit`, `openai`, `stripe`, `requests`, `Pillow`, `replicate`, `bcrypt`, `python-dotenv` | Behalten — aktiv genutzt |
| `moviepy` / `psycopg2` | Nicht in requirements (korrekt) |

### Behalten — aktive Test-Tools

| Datei | Zweck |
|-------|--------|
| `tools/test_football_feed.py` | Schnell-Smoke Topspiele/Alle API |
| `tools/test_all_outputs.py` | Vollständiger Repo-Smoke |
| `tools/dump_football_outputs.py` | Feed-Dump alle Zeitfilter |

---

## Smoke-Test Ergebnisse (2026-06-03)

| Test | Ergebnis |
|------|----------|
| `python -m py_compile .` | **PASS** (58 Dateien) |
| `database.ensure_db_ready()` | **PASS** |
| `ui.py` Football DEFAULTS | **PASS** (8 Keys) |
| `tools/test_football_feed.py` | **PASS** (Whitelist OK; 0 Spiele = API/Season lokal) |
| `tools/test_all_outputs.py` | **PASS** (nach BOM-Fix) |

### Football-Ausgaben (typisch ohne Paid API / Sommerpause)

```
displayed_topspiele_count=0
displayed_allspiele_count=0
topspiele_banner='Heute keine Topspiele verfügbar.'
all_banner='Aktuell keine API-Spiele für diesen Zeitraum.'
OK topspiele whitelist only
```

Mit API-Cache (Paid Key): **Alle API** liefert bis 50 Spiele; **Topspiele** nur Whitelist-Ligen.

---

## Phase 4 — abgeschlossen

- [x] Sidebar single component (`ui/sidebar.py`, 230px)
- [x] Header 64px, Dashboard minimal
- [x] Football strict feed (`football_feed.py`)
- [x] Session-State Football Keys (`ui.py` DEFAULTS + `_ensure_football_session`)
- [x] `docs/ai/*` Single Source of Truth
- [x] Global Cleanup + Requirements
- [x] Smoke-Tests + Report

---

## Offen (nicht Teil dieser TODO)

Siehe [ROADMAP.md](ROADMAP.md): Railway ENV, Stripe Yearly, E2E Playwright, Legal-Texte.

---

*Bei nächsten Änderungen: Metriken und Smoke-Ergebnisse hier patchen, nicht neu anlegen.*
