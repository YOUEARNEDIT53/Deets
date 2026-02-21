# Deets System — Deployment Guide

## Option 1: Deploy to Render (Recommended)

### Step 1: Push to GitHub

```bash
cd ~/.openclaw/workspace/deets-system

# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit: Deets POC"

# Add your GitHub repo
git remote add origin https://github.com/YOUR_USERNAME/deets-system.git
git branch -M main
git push -u origin main
```

### Step 2: Create Render Service

1. Go to https://render.com
2. Sign up / Log in
3. Click **New** → **Web Service**
4. Select **Connect a repository** → Choose `deets-system`
5. Fill in:
   - **Name:** `deets-system`
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
   - **Instance type:** Free (upgrade to Standard $7/mo later)

### Step 3: Add Environment Variables

In Render dashboard, go to **Environment**:

```
ANTHROPIC_API_KEY = sk-ant-[your-key-here]
```

Optional (for SMS):
```
TWILIO_ACCOUNT_SID = [your-sid]
TWILIO_AUTH_TOKEN = [your-token]
TWILIO_PHONE_NUMBER = +1234567890
```

### Step 4: Deploy

Click **Create Web Service**. Render will:
1. Clone your repo
2. Run `pip install -r requirements.txt`
3. Start `gunicorn app:app`
4. Provide you a live URL: `https://deets-system.onrender.com`

**⏱️ First deploy takes 2-3 minutes.**

### Step 5: Test

- Visit `https://deets-system.onrender.com`
- Click **Get Started**
- Enter phone, name, pick topics
- You'll be redirected to dashboard
- Click topic buttons to trigger deets

---

## Option 2: Run Locally (for testing)

### Setup
```bash
cd ~/.openclaw/workspace/deets-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env
cp .env.example .env
# Edit .env, add ANTHROPIC_API_KEY
```

### Run
```bash
python app.py
```

**URL:** http://localhost:5000

---

## Option 3: Deploy to Railway, Heroku, or Other

The `Procfile` is compatible with most platforms:

**Railway:**
- Create project → Connect GitHub → Select `deets-system`
- Add `ANTHROPIC_API_KEY` env var
- Deploy (automatic)

**Heroku (deprecated but still works):**
```bash
heroku login
heroku create deets-system
git push heroku main
heroku config:set ANTHROPIC_API_KEY=sk-ant-...
```

---

## Customizing for Different Hosts

### If Running on Your Own Server

```bash
# Install gunicorn
pip install gunicorn

# Run
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Or use screen/tmux for background
screen -S deets
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:8000 app:app
# Ctrl+A, D to detach
```

### If Running on Raspberry Pi

```bash
# Reduce workers (Pi has limited RAM)
gunicorn -w 2 -b 0.0.0.0:8000 app:app

# Or use waitress (lighter weight)
pip install waitress
waitress-serve --port 8000 app:app
```

---

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
# Make sure venv is activated: source venv/bin/activate
```

### "ANTHROPIC_API_KEY not set"
```bash
# Local: add to .env
# Render: add to Environment vars
# Check it's there: echo $ANTHROPIC_API_KEY
```

### Database locked error
```bash
# SQLite gets locked with many concurrent writes
# For Phase 1 (2 users): not an issue
# Phase 2 (50+ users): upgrade to PostgreSQL on Render
# In app.py, change:
# conn = sqlite3.connect(DB_PATH)
# To use: import psycopg2, update DATABASE_URL
```

### Render free tier resets after 15 min inactivity
- Upgrade to Standard ($7/mo) to keep it running 24/7
- For POC testing: free tier is fine (just refreshes the page)

---

## Monitoring & Logs

### Render Dashboard
- Go to your service
- **Logs** tab shows real-time console output
- **Metrics** shows CPU, memory, requests

### Local Testing
```bash
# Run with debug logging
FLASK_ENV=development FLASK_DEBUG=1 python app.py
```

---

## Security Notes

### API Keys
- Never commit `.env` to git (it's in `.gitignore`)
- Use Render's **Environment** section for production keys
- Rotate API keys periodically

### Database
- Phase 1: SQLite is fine (only you + Jim)
- Phase 2: Switch to PostgreSQL for security + reliability
- Never expose `deets.db` publicly

### Phone Numbers
- Don't log to console in production
- Store encrypted if you scale to many users
- Comply with GDPR/CCPA for data retention

---

## Scaling Strategy

**Phase 1 (2 users, free):**
- Render free tier
- SQLite database
- Cost: ~$10/mo (API only)

**Phase 2 (50 users, starter):**
- Render Standard ($7/mo)
- Neon PostgreSQL free tier ($0)
- Cost: ~$50/mo (API + hosting)

**Phase 3 (1K+ users, growth):**
- Render Standard + caching layer
- PostgreSQL Launch ($5/mo)
- Add Redis for session caching
- Cost: ~$150/mo

**Phase 4 (10K+ users, production):**
- Render Pro ($115+/mo)
- PostgreSQL Scale ($20+/mo)
- CloudFlare for DDoS protection
- Cost: ~$500-2K/mo

---

## Next: Automation (CRON)

Once live, add scheduled agent runs:

```python
# In app.py, add CRON support:
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def daily_deet_job(user_id, topic):
    """Run agent, send SMS"""
    deet = research_and_score(topic, temp)
    deliver_deet_sms(user.phone, deet)

# Schedule Chris's sports deet every morning at 9 AM
scheduler.add_job(
    lambda: daily_deet_job(1, 'Sports'),
    'cron',
    hour=9,
    minute=0
)

scheduler.start()
```

Or use Render's CRON service (easier).

---

## Once Live: Quick Checklist

- [ ] URL is live and loading
- [ ] Can create account with phone + name
- [ ] Can select topics
- [ ] Dashboard shows preference controls
- [ ] Click topic button → triggers agent → shows deet
- [ ] Deet shows headline, summary, credibility score, smell test flags
- [ ] Thumbs up/down buttons work
- [ ] Share button generates link
- [ ] Share link shows teaser view
- [ ] No errors in Render logs

---

## Quick Deployment (TL;DR)

1. Push to GitHub
2. Render → New Web Service → Connect repo
3. Set `ANTHROPIC_API_KEY` env var
4. Deploy (automatic)
5. Visit URL, sign up, test topics
6. Done!

---

**Estimated setup time:** 5 minutes  
**Estimated first deploy:** 2-3 minutes  
**Total:** 7-8 minutes from GitHub push to live
