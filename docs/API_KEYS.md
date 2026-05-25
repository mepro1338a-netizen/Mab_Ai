# MaByte — API Keys

## Pflicht (Kern-App)

| Key | Woher | URL |
|-----|-------|-----|
| `OPENAI_API_KEY` | OpenAI Platform | https://platform.openai.com/api-keys |
| `APP_BASE_URL` | Deine Railway-URL | z.B. `https://mabai-production.up.railway.app` |

## OAuth Login

| Key | Woher | URL |
|-----|-------|-----|
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google Cloud Console → OAuth 2.0 | https://console.cloud.google.com/apis/credentials |
| `META_APP_ID` / `META_APP_SECRET` | Meta for Developers → App | https://developers.facebook.com/apps/ |
| `TIKTOK_CLIENT_KEY` / `TIKTOK_CLIENT_SECRET` | TikTok for Developers → Login Kit | https://developers.tiktok.com/ |
| `OAUTH_STATE_SECRET` | Selbst generieren (32+ Zeichen) | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `GOOGLE_OAUTH_REDIRECT_URI` | Optional, sonst automatisch | `https://mabyte.de/oauth/google/callback` |

**Google Cloud Console → Authorized redirect URIs:**

- Produktion: `https://mabyte.de/oauth/google/callback`
- Lokal: `http://localhost:8501/oauth/google/callback`

`APP_BASE_URL` muss zur öffentlichen Domain passen (z.B. `https://mabyte.de`).

Instagram/TikTok Redirect (falls genutzt): `{APP_BASE_URL}/`

## Football Live Data

| Key | Woher | URL |
|-----|-------|-----|
| `FOOTBALL_API_KEY` | API-Football (api-sports.io) | https://www.api-football.com/ |

## Payments (Stripe)

| Key | Woher | URL |
|-----|-------|-----|
| `STRIPE_SECRET_KEY` | Stripe Dashboard → Developers → API keys | https://dashboard.stripe.com/apikeys |
| `STRIPE_WEBHOOK_SECRET` | Stripe → Webhooks → Signing secret | https://dashboard.stripe.com/webhooks |
| `STRIPE_PRICE_PRO` / `GRAND` / `ELITE` | Stripe → Products → Price IDs | https://dashboard.stripe.com/products |
| `STRIPE_PRICE_FOOTBALL_*` | Optional Football-Pläne | gleich |

## Optional (Media / Video / Music)

| Key | Woher | URL |
|-----|-------|-----|
| `REPLICATE_API_TOKEN` | Replicate | https://replicate.com/account/api-tokens |
| `STABILITY_API_KEY` | Stability AI | https://platform.stability.ai/account/keys |
| `FAL_KEY` | fal.ai | https://fal.ai/dashboard/keys |
| `SUNO_API_URL` / `SUNO_API_KEY` | Nur wenn legaler Provider | variabel |

## Optional (Email)

| Key | Woher | URL |
|-----|-------|-----|
| `RESEND_API_KEY` | Resend | https://resend.com/api-keys |

## Railway

Alle Keys als **Variables** im Railway Service setzen (nicht committen).
