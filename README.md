# Mabyte V13 API Ready

## Start
```bash
pip install -r requirements.txt
copy .env.example .env
python main.py
```

## Admin Login
Username: `admin`
Password: `admin`

## API Keys eintragen
Öffne `.env` und trage deine Keys ein:

```env
OPENAI_API_KEY=sk-...
STABILITY_API_KEY=...
REPLICATE_API_TOKEN=...
FAL_KEY=...
STRIPE_SECRET_KEY=sk_test_...
```

## Provider auswählen
```env
IMAGE_PROVIDER=openai
VIDEO_PROVIDER=replicate
MUSIC_PROVIDER=openai_prompt
```

Optionen:
- IMAGE_PROVIDER: `openai` oder `stability`
- VIDEO_PROVIDER: `replicate` oder `fal`
- MUSIC_PROVIDER: `openai_prompt`, `replicate` oder `fal`

## Video Token Profit System
- Fast: 250 Tokens
- Quality: 500 Tokens
- Premium: 900 Tokens

Grand = 3000 Tokens:
- Max 12 Fast Videos
- Max 6 Quality Videos
- Max 3 Premium Videos

## Wichtig
Wenn ein API-Key leer ist, zeigt die App eine klare Fehlermeldung statt zu crashen.


## V13.2 Support/Admin Inbox
- Users can send Support messages.
- Admin Panel has Support Inbox with unread counter.
- Admins/Moderators can mark read/unread, close/open and delete support messages.
- Admin Team Chat added.
- Account tier/plan and role can be changed in Admin Panel.
- Codes and Payment History remain Admin-only.

## V13.3 Media Ready
- TikTok/Instagram Content removed.
- Script Generator removed.
- Music Generator is API-ready for real audio/song generation:
  - Replicate MusicGen
  - fal.ai audio endpoints
  - optional Suno-compatible custom API wrapper
- Short Reels Creator now creates short vertical AI videos using the video provider.
