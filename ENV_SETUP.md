# MaByte Environment Setup

Kopiere `.env.example` nach `.env` (lokal) oder setze Variablen in Railway.

## Required (Production Beta)
| Variable | Beschreibung |
|----------|--------------|
| `APP_BASE_URL` | Öffentliche URL, z.B. `https://mabyte.de` |
| `DATA_DIR` | Persistenz, z.B. `/data` auf Railway |
| `OAUTH_STATE_SECRET` | HMAC für OAuth State (min. 32 Zeichen) |

## Auth (Google)
| Variable | Beschreibung |
|----------|--------------|
| `GOOGLE_CLIENT_ID` | OAuth Client ID |
| `GOOGLE_CLIENT_SECRET` | OAuth Secret |
| `GOOGLE_OAUTH_REDIRECT_URI` | Optional, volle URL — muss Console matchen |

## AI
| Variable | Beschreibung |
|----------|--------------|
| `OPENAI_API_KEY` | Chat, Coding, Fallback Images |
| `OPENAI_*_MODEL` | Modell pro Tier (siehe `.env.example`) |

## Football
| Variable | Beschreibung |
|----------|--------------|
| `FOOTBALL_API_KEY` | API-Football Key |
| `FOOTBALL_API_CACHE_TTL` | Default 300 |
| `FOOTBALL_API_LIVE_CACHE_TTL` | Default 60 |

## Stripe
| Variable | Beschreibung |
|----------|--------------|
| `STRIPE_SECRET_KEY` | API Secret |
| `STRIPE_WEBHOOK_SECRET` | Webhook (separater Service) |
| `STRIPE_PRICE_PRO` / `GRAND` / `ELITE` | MaByte Pläne |
| `STRIPE_PRICE_FOOTBALL_*` | Football Pläne |
| `STRIPE_SUCCESS_URL` / `CANCEL_URL` | Checkout Return |

## Optional
| Variable | Beschreibung |
|----------|--------------|
| `REPLICATE_API_TOKEN` | Video/Music |
| `FAL_KEY` | Video/Music alt |
| `STABILITY_API_KEY` | Images |
| `RESEND_API_KEY` | E-Mail Verification (später) |

## Validierung
```powershell
cd c:\mab_upload
python -m py_compile main.py ui.py ui_core.py pages\*.py services\os_guide.py ui\*.py
python -c "from database import ensure_db_ready; print(ensure_db_ready())"
```

## Fehlende Keys — Verhalten
- **OPENAI**: Chat zeigt Hinweis, kein Crash
- **FOOTBALL_API_KEY**: Football Live-Daten deaktiviert, UI-Fallback
- **STRIPE**: Premium-Buttons disabled + Warning
- **GOOGLE**: OAuth-Button ausgeblendet / Fehlermeldung
