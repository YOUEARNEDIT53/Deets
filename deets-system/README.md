# Deets — Viral Information Spreading System

## Phase 1: Core Loop (DROP → VALIDATE → CHALLENGE → PASS → TRAIL)

A deet moves through people, gaining or losing credibility at every touch. The **PASS is the product**. The **TRAIL is the proof**.

### What Works

✅ **DROP** — User creates a claim and sends to recipients  
✅ **VALIDATE** — Receiver validates (+0.3 score, weighted by credibility)  
✅ **CHALLENGE** — Receiver challenges (-0.3 score, with optional note)  
✅ **PASS** — Forward deet to new recipients (+0.1 soft validation)  
✅ **TRAIL** — Immutable history of all events (who touched what, when, why)

### Deploy to Internet (Render)

**1-Click Deploy (Coming Soon):**

For now, manual deploy:

1. Go to [render.com](https://render.com) and sign up (free)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account, select `YOUEARNEDIT53/Deets`
4. Fill in:
   - **Name:** `deets`
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `python app.py`
5. Add environment variable:
   - **Key:** `ANTHROPIC_API_KEY`
   - **Value:** (your Anthropic API key)
6. Click **"Create Web Service"**
7. Wait 2-3 minutes for deployment

**Your live URL:** `https://deets-xxxx.onrender.com`

**Password:** `deets2026`

### Test Locally

```bash
cd deets-system
python app.py
# Visit http://localhost:5000
# Password: deets2026
```

### Architecture

**Backend:**
- Flask (Python)
- SQLite database
- Anthropic Claude (for agent seeding, Phase 2)

**Database:**
- `users` — credibility scores, interaction counts
- `deets` — claims, current score, state
- `trail_events` — immutable log (drop/view/validate/challenge/pass)
- `topics` — categories users follow

**API Endpoints:**
- `POST /api/deet/drop` — Create deet, send to recipients
- `POST /api/deet/<id>/validate` — Validate claim
- `POST /api/deet/<id>/challenge` — Challenge claim with note
- `POST /api/deet/<id>/pass` — Forward to new recipients
- `GET /api/deet/<id>/trail` — Full event history

### Score Calculation

```
VALIDATE: +0.3 * (validator_credibility / 5.0)
CHALLENGE: -0.3 * (challenger_credibility / 5.0)
PASS: +0.1 * (passer_credibility / 5.0)
```

Score range: 0.0 - 10.0 (clamped)

### State Transitions

- **fresh:** < 10 interactions
- **spreading:** 10-99 interactions
- **hot:** 100+ interactions AND score > 7.0
- **confirmed:** score > 8.5 AND 85%+ validation rate
- **disputed:** balanced validate/challenge ratio
- **debunked:** score < 3.0 AND 20+ challenges
- **faded:** no interaction in 48 hours

### Next (Phase 2)

- [ ] Feed UI (show deets, action buttons)
- [ ] Trail visualization (chain display)
- [ ] Teaser page (unauthenticated view + install CTA)
- [ ] Agent seeding (Claude generates deets autonomously)
- [ ] Push notifications
- [ ] User credibility update algorithm
- [ ] Leaderboard

### Files

- `app.py` — Flask backend (450 lines, core logic)
- `templates/` — HTML templates (landing, setup, login, dashboard)
- `requirements.txt` — Python dependencies
- `Procfile` — Heroku/Render deployment config
- `render.yaml` — Render-specific config

### Team

- **Product:** Chris (youearnedit53)
- **Build:** Genny (AI agent)

---

**Status:** Phase 1 complete. All core endpoints tested and working. Ready for UI testing on cellular.
