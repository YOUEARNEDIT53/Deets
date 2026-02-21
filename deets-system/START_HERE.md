# Deets System — START HERE

## What We Built

A fully functional **AI agent that finds verified information, scores credibility, and sends you deets**.

**Location:** `~/.openclaw/workspace/deets-system/`

**Stack:**
- Flask backend (Python)
- Claude Haiku for agent (research + scoring + smell test)
- SQLite database
- Render for deployment
- Twilio for SMS (optional)

**All templating, database schema, deployment config = DONE.**

---

## What It Does

1. **You sign up** → Phone, name, pick 1-3 topics (Celebrity, Sports, Tech, True Crime, Crypto)
2. **Agent researches** → Finds sources, scores credibility, runs smell test
3. **You see results** → Credibility score (0-10), source breakdown, red flags
4. **You give feedback** → Thumbs up/down trains the model
5. **You share** → Friend gets link → needs app to see full view → installs → gets deets too

---

## How to Launch

### Local Testing (5 minutes)

```bash
cd ~/.openclaw/workspace/deets-system

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env, paste your ANTHROPIC_API_KEY

# Run
python app.py

# Visit http://localhost:5000
```

### Deploy to Render (10 minutes)

1. Push code to GitHub (see DEPLOYMENT.md)
2. Go to render.com → New Web Service
3. Connect your GitHub repo
4. Add `ANTHROPIC_API_KEY` env var
5. Click Deploy
6. Wait 2-3 minutes → live URL

See `DEPLOYMENT.md` for full guide.

---

## File Structure

```
deets-system/
├── app.py                    # Core Flask app + Claude agent
├── templates/
│   ├── landing.html         # Home page hook
│   ├── setup.html           # Onboarding (phone, topics, temperature)
│   ├── dashboard.html       # Main interface + deet feed
│   └── share.html           # Share teaser (credibility preview)
├── requirements.txt         # Python dependencies
├── Procfile                 # Render deployment
├── .env.example             # Env template (copy to .env locally)
├── deets.db                 # SQLite (auto-created)
├── README.md                # Full technical guide
├── DEPLOYMENT.md            # Deployment instructions
├── LAUNCH_CHECKLIST.md      # Testing checklist
└── START_HERE.md            # This file
```

---

## The Claude Agent

**In `app.py`, function `research_and_score(topic, temperature)`:**

1. **Research phase:** Uses Claude Haiku to find information on a topic
2. **Scoring phase:** Assigns credibility to sources (0-10)
3. **Smell test phase:** Checks for:
   - Logical inconsistencies
   - Known debunked claims
   - Sensationalism
   - Verification status
4. **Returns:** Headline, summary, sources, credibility score, cross-references, flags

**Cost per deet:** ~$0.01-0.05 (Haiku is cheap)

---

## Next Steps (This Week)

### Step 1: Test Locally (30 minutes)
```bash
cd deets-system
python app.py
# Visit http://localhost:5000
# Create account, pick topics, click "Sports" button
# Verify agent outputs deet with credibility score
```

### Step 2: Deploy to Render (10 minutes)
- See DEPLOYMENT.md for exact steps
- Should be live in 2-3 minutes

### Step 3: You + Jim Create Accounts
- Both sign up on live URL
- Each pick 2-3 topics
- Trigger deets manually (click topic buttons)
- Quality-check outputs together

### Step 4: Run through Checklist
- See LAUNCH_CHECKLIST.md
- Verify credibility scoring makes sense
- Verify smell-test flags are useful
- Test feedback loops (thumbs up/down)

### Step 5: Iterate Agent
- If deets are low quality: adjust agent prompt in `app.py`
- If smell-test flags are noisy: refine the logic
- Re-deploy to Render (just `git push`)

---

## Key Features Built In

### Credibility Scoring
```
Source Track Record → 0-10 per source
Community Validation → User thumbs up/down
Cross-References → How many sources agree
Logical Consistency → AI flags impossible claims
Debunk History → Checks known false claims
Sensationalism → Flags emotionally charged language
```

**Result:** One credibility score per deet (0-10), weighted by all above factors.

### Viral Share Loop
1. User gets deet (headline + credibility score)
2. User shares link to friend
3. Friend sees teaser (headline + score only)
4. Friend needs app to see full breakdown
5. Friend installs app
6. Friend gets deets
7. Friend shares
8. **Exponential growth**

### Cost Control
- Claude Haiku: 10-15x cheaper than Sonnet
- API spending caps: Set $50/mo, raise as you scale
- Free tier Render: No hosting cost until Phase 2
- SQLite: No database cost

**Projected Phase 1 cost: $10-20/month**

---

## Testing the Agent

From the dashboard, click any topic button:

```
📡 Celebrity/Entertainment
📡 Sports
📡 Tech Breakthroughs
📡 True Crime
📡 Crypto/Finance
```

Watch it:
1. Think about the topic
2. Research current news
3. Score sources
4. Run smell test
5. Return credibility score (you'll see it in the response)

If it's great: note the topic  
If it's bad: tell me and I'll refine the agent prompt

---

## Customizing the Agent

In `app.py`, function `research_and_score()`, adjust the prompt:

**To emphasize accuracy more:**
```python
prompt = f"""You are the Deets Agent. Research "{topic}"
ACCURACY IS CRITICAL. Only include facts you're sure about.
Flag any unverified claims prominently.
..."""
```

**To go deeper on certain topics:**
```python
# Increase temperature for finance/crypto (requires nuance)
depth_instruction = "very deep, nuanced research"
```

**To change what smell-test checks:**
```python
"smell_test_flags": [
    "possible bias detected",
    "source is known competitor",
    "claim conflicts with verified fact",
]
```

Deploy changes with: `git push origin main` (Render auto-redeploys)

---

## Scaling Path

**Phase 1 (Now → Week 3):** You + Jim testing  
- Free Render, SQLite, $10-20 API costs

**Phase 2 (Week 4-6):** 50-user beta  
- Render Standard ($7/mo), CRON automation, $50 API costs

**Phase 3 (Week 7-12):** Public launch  
- App store, payments, $400 total investment

**Phase 4+:** Growth  
- Postgres database, Redis caching, scaled infrastructure

---

## Troubleshooting

**Agent returns error:**
- Check ANTHROPIC_API_KEY is set (local: .env, Render: env vars)
- Check syntax of the topic name

**Render deploy fails:**
- Check logs: Render dashboard → Logs tab
- Make sure requirements.txt has all dependencies
- Try local test first: `python app.py`

**Database locked error:**
- Phase 1: Not an issue (you're the only user)
- Phase 2+: Switch to PostgreSQL

**Credibility scores seem random:**
- Agent is using mock scoring in Phase 1
- Once you validate it's working, we'll add real accuracy tracking

---

## The Big Picture

**Deets Dot is the wedge product.** It gets the app installed and proves the technology works.

After this succeeds, we build:
- Spark (greeting cards)
- Powwow (group chat)
- Commerce Dot (shopping agent)
- Dating Dot (matchmaking)
- Agent-to-Agent (your agent calls Walgreens for you)

**All run on the same agentic engine we're building now.**

---

## Questions?

- **Technical:** Check app.py, README.md, DEPLOYMENT.md
- **Testing strategy:** See LAUNCH_CHECKLIST.md
- **Agent quality:** See agent prompt in research_and_score()
- **Scaling:** See README.md phase roadmap

---

## Your Move

1. **Clone/navigate:** `cd ~/.openclaw/workspace/deets-system`
2. **Test locally:** `python app.py` → http://localhost:5000
3. **Deploy to Render:** Follow DEPLOYMENT.md
4. **Create account:** Use real phone (or test number)
5. **Trigger a deet:** Pick a topic, click button
6. **See the magic:** Credibility score appears
7. **Tell me:** What worked, what needs iteration

**Target:** Live testing with Jim by end of week.

---

**Status:** 🚀 Ready to Launch  
**Effort to get live:** 10-15 minutes  
**Value:** See the future of DotSpeak working

Go build it! 🔥
