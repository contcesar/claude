# Content Studio

YouTube content production system for the journaling niche. Monitors competitor channels, identifies outlier videos, generates scripts and LinkedIn posts.

## Stack
- Python 3.11+
- Flask (web UI)
- YouTube Data API v3
- Anthropic API (claude-opus-4-7)
- Slack Incoming Webhooks

## Running the App
```bash
pip install -r requirements.txt
python app.py          # Web UI at http://localhost:5000
python scheduler.py    # Runs daily Slack digest (also runs once immediately)
```

## Key Files
- `brand_blueprint.md` — Voice, audience, content pillars. Update this as your channel evolves.
- `config/channels.json` — Competitor channels to monitor. Add/remove anytime.
- `data/` — Cached videos, scripts, LinkedIn posts (gitignored, generated at runtime)
- `.env` — API keys (never commit this)

## Architecture
```
agents/monitor.py      YouTube Data API: fetches videos, calculates outlier scores
agents/script_gen.py   Claude API: generates scripts using 7-step hook framework
agents/linkedin.py     Claude API: generates 6 LinkedIn post angles
agents/notifier.py     Slack webhook: sends daily digest
app.py                 Flask web interface
scheduler.py           Daily cron: scan channels + send Slack digest
```

## Outlier Score
`video_views / channel_avg_views` — score of 2.0 means the video got 2x the channel average.
Anything above 2.0 is flagged as an outlier worth adapting.

## Adding Competitor Channels
Edit `config/channels.json`. Use the YouTube handle without `@`:
```json
{"name": "Channel Name", "handle": "channelhandle"}
```

## Updating the Brand Blueprint
Edit `brand_blueprint.md` directly, or tell Claude Code what changed and it will update the file.
The brand blueprint is loaded into every script and LinkedIn generation call — keeping it accurate directly improves output quality.

## Niche
Journaling for business owners, entrepreneurs, agency owners. Adults 30–50.
