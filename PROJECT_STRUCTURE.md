# MaByte Project Structure

```
mab_upload/
├── main.py                 # Railway entry → ui.py
├── ui.py                   # Router, auth gate, error boundaries
├── ui_core.py              # Sidebar, CSS, nav, logout
├── config.py               # Plans, ENV, paths
├── database.py             # DB facade
├── logger.py               # Structured JSON logs
├── security.py             # Rate limits, validation
├── oauth_service.py        # OAuth state HMAC
├── payments.py             # Stripe checkout
│
├── db/
│   ├── core.py             # Schema, init_db
│   ├── users.py            # Auth, roles
│   ├── support.py          # Tickets + replies
│   ├── errors.py           # app_error_logs
│   ├── admin_stats.py      # Platform metrics
│   └── ...
│
├── services/
│   ├── session_auth.py     # Session rotation, logout
│   ├── access_control.py   # Server-side plan/admin gates
│   ├── reliability.py      # Retries, safe_call
│   ├── os_guide.py         # Mab AI sidebar guide
│   ├── football_access.py  # Football feature gates
│   └── football_service.py # API client + cache
│
├── ui/
│   ├── design_system.py    # Global premium CSS
│   ├── premium_foundation.py
│   ├── error_boundary.py
│   ├── os_helper.py
│   └── seo.py
│
├── pages/
│   ├── auth.py             # Login, OAuth, register
│   ├── home.py             # Mission Control + launch sections
│   ├── legal.py            # Impressum, AGB, …
│   ├── admin.py            # Control panel
│   └── ...
│
└── docs/                   # GOOGLE_OAUTH, RAILWAY, …
```

## Data flow
1. `main.py` → `ensure_db_ready()`
2. `ui.py` → auth or `enforce_active_session()`
3. Page handler via `safe_render()`
4. Premium/Football: `football_access` + DB user record

## Logs
`{DATA_DIR}/logs/mabyte.log` — JSON lines, secrets redacted.
