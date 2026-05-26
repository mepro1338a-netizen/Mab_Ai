# Video Generation & Auto-Publishing Engine

## ENV (Railway / `.env`)

| Variable | Pflicht | Beschreibung |
|----------|---------|--------------|
| `OPENAI_API_KEY` | Ja (Paket-Metadaten) | Titel, Caption, Hashtags |
| `VIDEO_PROVIDER` | Nein | `mock` \| `replicate` \| `fal` (Default: `mock`) |
| `REPLICATE_API_TOKEN` | Für Replicate | |
| `REPLICATE_VIDEO_MODEL` | Für Replicate | z.B. `kwaivgi/kling-v1.6-standard` |
| `REPLICATE_REELS_MODEL` | Optional | Fallback auf VIDEO_MODEL |
| `FAL_KEY` | Für FAL | |
| `FAL_VIDEO_ENDPOINT` | Für FAL | fal.ai Model Endpoint URL |
| `OAUTH_STATE_SECRET` | Für Token-Speicherung | OAuth + verschlüsselte Social Tokens |
| `VIDEO_TOKEN_ENCRYPT_KEY` | Optional | Überschreibt Secret für Token-Verschlüsselung |
| `YOUTUBE_OAUTH_CLIENT_ID` | OAuth | oder `GOOGLE_CLIENT_ID` |
| `META_APP_ID` | Instagram OAuth | |
| `TIKTOK_CLIENT_KEY` | TikTok OAuth | |

## Test

```bash
python -m py_compile db/video_engine.py services/video_engine.py services/video_providers/*.py ui/video_engine_ui.py
python -c "from db.video_engine import init_video_engine_tables; init_video_engine_tables(); print('ok')"
python -c "from services.video_providers import provider_status; print(provider_status())"
```

## Zwei Qualitätsstufen (Token-Ökonomie)

| Modus | Kosten für dich | Tokens User | Qualität |
|-------|-----------------|-------------|----------|
| **MaByte Studio** | ~0 (FFmpeg) | 22–35 | Branded Export, kein KI-Clip |
| **KI-Video** | Replicate/FAL API | 90–180+ | Echte KI-Szene aus Prompt |
| **KI-Video HD** | höhere API | +45% Tokens | Schärfere Prompts, länger |

`VIDEO_PROVIDER=auto` wählt Replicate → FAL → Studio.

## Pläne

- **Free:** MaByte Studio (kurz), Creator Tools
- **Pro:** KI-Video + Queue + Download
- **Grand/Elite + Automation Unlock:** Schedule, Auto-Publishing-Vorbereitung

## API-Risiken

- **TikTok:** Content Posting API erfordert oft Partner-Freigabe; ohne Freigabe nur `ready_to_publish`.
- **Instagram:** Graph API + App Review für Reels Publishing; Business/Creator Account nötig.
- **YouTube:** Shorts Upload über YouTube Data API v3 + OAuth Scopes; Quota-Limits beachten.
