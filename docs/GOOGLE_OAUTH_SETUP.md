# Google OAuth — MaByte Setup

## Error 400 `invalid_request` / „Access blocked“

Häufigste Ursachen:

1. **Redirect URI stimmt nicht exakt überein** (Slash, http vs https, falsche Domain)
2. **OAuth Consent Screen = Testing** — deine Gmail muss unter **Test users** stehen
3. **Falscher Client-Typ** — muss **Web application** sein, nicht Desktop
4. **APP_BASE_URL** in Railway zeigt noch auf `*.railway.app` statt `https://mabyte.de`

## Railway ENV

```env
APP_BASE_URL=https://mabyte.de
GOOGLE_CLIENT_ID=....apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
OAUTH_STATE_SECRET=<32+ random hex>
```

Optional (nur wenn du einen festen Pfad willst):

```env
GOOGLE_OAUTH_REDIRECT_URI=https://mabyte.de/
# oder mit Pfad (Proxy muss auf Streamlit zeigen):
# GOOGLE_OAUTH_REDIRECT_URI=https://mabyte.de/oauth/google/callback
```

**Standard ohne Override:** Redirect = `https://mabyte.de/` (Streamlit-kompatibel).

## Google Cloud Console

### OAuth consent screen

- User type: **External**
- Publishing status: **Testing** (bis Verifizierung)
- **Test users:** `maksigewinnt@gmail.com` (jede Gmail die einloggen soll)

### Credentials → OAuth 2.0 Client IDs → Web application

**Authorized JavaScript origins:**

- `https://mabyte.de`
- `http://localhost:8501` (lokal)

**Authorized redirect URIs** (beide eintragen wenn unsicher):

- `https://mabyte.de/`
- `https://mabyte.de/oauth/google/callback`
- `http://localhost:8501/`

Die App zeigt unter Login → „Google Login funktioniert nicht?“ die **aktive Redirect URI**.

## Nach Deploy testen

1. Login-Seite → Mit Google anmelden
2. Google-Konto wählen (muss Test user sein)
3. Zurück auf MaByte mit `?code=...&state=...` in der URL
