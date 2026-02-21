# The Deets System — Phase 1 POC

AI agent that finds what's true, scores who's credible, and sends you the deets before anyone else.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web UI (Flask)                            │
│  Landing → Setup → Dashboard → Share Links                  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Topic Agent (Claude)                       │
│  Research → Score Sources → Smell Test → Store Result       │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    SQLite Database                           │
│  Users | Preferences | Deets | Source History | Debunks    │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   SMS Delivery (Twilio)                      │
│  Send scored briefings to user phones                        │
└─────────────────────────────────────────────────────────────┘
```

## Features

### Core Agent Capabilities
- **Topic research** via Claude Haiku (cost-optimized)
- **Credibility scoring** (source track record + community validation)
- **Cross-reference detection** (how many sources confirm)
- **Smell test logic** (logical inconsistencies, debunk history, sensationalism)
- **Debunk checking** (against known false claims)

### UI/UX
- **Landing page** — Hook (no typing)
- **Setup flow** — Phone, name, 1-5 topics, research depth (temperature dial)
- **Dashboard** — View all deets, adjust preferences, test topics on demand
- **Share links** — Teaser view (headline + credibility), full view requires app install

### Database
- Users + phone numbers
- Topic preferences (temperature, frequency, filters)
- Deets history (headline, summary, sources, credibility, community votes, smell test flags)
- Source credibility history (tracks accuracy over time)
- Known debunked claims registry

## Quick Start (Local)

### 1. Clone & Setup
```bash
cd ~/.openclaw/workspace/deets-system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env, add your ANTHROPIC_API_KEY
```

### 3. Run Locally
```bash
python app.py
# Visit http://localhost:5000
```

## Deployment to Render

### 1. Push to GitHub
```bash
cd ~/.openclaw/workspace/deets-system
git init
git add .
git commit -m "Initial commit: Deets POC"
git remote add origin https://github.com/YOUR_USERNAME/deets-system.git
git push -u origin main
```

### 2. Create Render Service
- Go to https://render.com
- New → Web Service
- Connect GitHub repo `deets-system`
- Set runtime: Python 3.11
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Add environment variable: `ANTHROPIC_API_KEY` = your key
- Deploy

### 3. Configure Twilio (Optional, for SMS)
- Get Twilio account at https://twilio.com
- Add `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` to Render env vars
- Update `deliver_deet_sms()` in `app.py` to actually call Twilio

## Phase 1 Focus

✓ Single user (you + Jim) testing daily
✓ Full smell-test logic operational
✓ Topic agent working end-to-end
✓ Manual trigger for testing
✓ Web dashboard + SMS delivery

## Next Steps (Phase 2)

- [ ] CRON automation (scheduled daily/weekly agent runs)
- [ ] Twilio SMS integration (real delivery)
- [ ] Onboarding UX polish
- [ ] Share mechanic (link teaser + viral loop)
- [ ] Beta user group (50 users)

## Topics (Seed for Testing)

1. **Celebrity/Entertainment** — Oscar predictions, Marvel releases
2. **Sports** — Super Bowl drama, tournament updates
3. **Tech Breakthroughs** — AI releases, new products
4. **True Crime** — Cold cases, legal proceedings
5. **Crypto/Finance** — Market moves, SEC news

## Cost Estimates

**Phase 1 (2-3 weeks, 2 users):**
- Render free tier: $0
- Claude Haiku: ~$2-5/mo
- Twilio (optional): ~$5/mo
- Total: ~$10

**Phase 2 (3 weeks, 50 users):**
- Render starter: ~$7/mo
- Claude Haiku: ~$15-20/mo
- Twilio: ~$5-20/mo
- Total: ~$50

## Key Decisions Made

- **Claude Haiku** for agent (10-15x cheaper than Sonnet)
- **SQLite** for Phase 1 (scales to hundreds of users, free)
- **Flask** (minimal, flexible, easy to iterate)
- **Render** (free tier to start, cheap scaling)
- **Full smell-test logic from Day 1** (builds credibility moat early)

## Files Structure

```
deets-system/
├── app.py                 # Main Flask app + Claude agent
├── requirements.txt       # Python dependencies
├── Procfile              # Render deployment config
├── render.yaml           # Alternative Render config
├── .env.example          # Environment variables template
├── deets.db             # SQLite database (auto-created)
├── templates/
│   ├── landing.html     # Home page
│   ├── setup.html       # User onboarding
│   ├── dashboard.html   # Main interface
│   └── share.html       # Share teaser view
└── README.md            # This file
```

## Running Agent Tests

From dashboard, click any topic button to manually trigger research:

```
📡 Celebrity/Entertainment
📡 Sports
📡 Tech Breakthroughs
📡 True Crime
📡 Crypto/Finance
```

Watch the agent:
1. Research the topic
2. Score sources
3. Run smell test
4. Store result
5. Display credibility score (0-10)

## Feedback Loop

Users can thumbs up/down each deet. This trains:
- Source credibility scores
- Community validation metrics
- Smell test accuracy

## Next: Automation

Once POC is solid, add CRON jobs so the agent:
1. Wakes at user's preferred frequency (daily, real-time, weekly)
2. Researches trending topics in their preferences
3. Scores credibility automatically
4. Sends SMS notification
5. User taps link → shares with friends → installs app

That's the viral loop.

---

**Built by:** Chris & Jim  
**Date:** February 2026  
**Status:** Phase 1 POC
