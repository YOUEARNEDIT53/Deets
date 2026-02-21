# MEMORY.md - Long-Term Memory

## 2026-02-18
- First session. Chris introduced himself.
- Identity established: I'm Genny — quick-witted, technical, problem-solver.
- Chris's focus: building agents and AI software.

## 2026-02-19 (continued)
- Built **Jupiter Home Finder** app — Flask + SQLite at `~/.openclaw/workspace/jupiter-homes/`, port 8765
  - Chris looking for 2BR/1BA ~1,200 sqft ≤$800k near parks/water in Jupiter FL
  - Pre-filtered search links (Zillow/Redfin/Realtor/Trulia/Homes.com), saved homes tracker, neighborhood scoring
- **Qwen outage lesson**: Switching main agent to `ollama/qwen3:30b-a3b` caused 1+ hour unresponsiveness. Reverted to Claude Opus. ARTEX PM agent still uses Qwen with Claude fallback. Test local models before switching primary.
- Pulse rebuilt as proper Flask + SQLite app (`~/.openclaw/workspace-artex-pm/pulse/`) on port 8090, with full PMI structure and all kickoff PPT data in 25+ DB tables
- Generated email-ready HTML report: `~/Downloads/ELT2000_Program_Report_20260219.html`
- Chris cannot access SharePoint/Teams directly — must download files to local machine

## 2026-02-19
- Created **ARTEX PM** agent (`artex-pm`) — AI co-pilot for ACR ARTEX ELT-2000 program.
- Model: `ollama/qwen3:30b-a3b` (local RTX 5090, 32GB VRAM). Fallback: Sonnet 4.6.
- Workspace: `~/.openclaw/workspace-artex-pm/` with full PMP knowledge base populated from `ELT2000Kickoff_2026.pptx`.
- Built **"Pulse"** — interactive PM dashboard tool at `workspace-artex-pm/dashboard/index.html` (served on port 8090).
  - Gantt chart from actual kickoff presentation, all fields editable, critical path editable, WBS with ADP coding (NNNNNN.NN format from ACR_ARTEX_Task_Coding.pptx), file repository, JSON export/import.
  - Program code: 9910. Ship target: 10/28/2027. COGS target: $750.
  - 17 named team members, 11 risks with owners, full cert plan (TSO-C126b, ETSO, C/S T.018/T.021).
- **Key flags:** No RF engineer assigned, 5-week CDR→test gap, FAA date (6/17) before CDR (9/16).
- Chris wants this to be a full standalone program that can load onto any PC, with interactive editing of all fields.

## 2026-02-21 - DotSpeak Launch: Deets System (PHASE 1 CORE LOOP BUILT)

### Session 4: CRITICAL REFRAME + PHASE 1 BUILD (Chris's spec)
**MAJOR PIVOT:** Rebuilt entire product focus from news feed → social viral loop.  
**THE PRODUCT:** Deets move through people (DROP → VALIDATE/CHALLENGE → PASS → TRAIL). Each interaction alters credibility. The PASS is the product. The TRAIL is the proof.

**COMPLETED:**
- ✅ **STEP 1 (Foundation):** Fixed Claude model (haiku-4-5-20251001), disabled spider, Flask runs clean on 0.0.0.0:8765
- ✅ **STEP 2 (DROP mechanic):** Core endpoint POST /api/deet/drop implemented with full logic:
  - User creates claim (max 280 chars) + picks topic + anonymous toggle + recipients
  - Creates deet with state "fresh", initial score 5.0 (or 3.0 if anonymous)
  - Records DROP event with recipients, CREATE VIEW events for each recipient
  - Tested end-to-end: Create users → Drop deet → Trail shows drop + view events ✅
- ✅ **VALIDATE endpoint:** Score formula: +0.3 * (validator_credibility / 5.0). Tested: Score went 5.0 → 5.3 ✅
- ✅ **CHALLENGE endpoint:** Score formula: -0.3 * (challenger_credibility / 5.0), with optional note
- ✅ **PASS endpoint:** Score formula: +0.1 * (passer_credibility / 5.0), logs PASS + VIEW events for recipients
- ✅ **TRAIL endpoint:** GET /api/deet/<id>/trail returns full event history with users, timestamps, notes, recipients

**Database schema (verified working):**
- `users`: id, display_name, phone, credibility_score, total_drops/validations/challenges/passes
- `deets`: id, claim_text, origin_type, origin_user_id, topic_id, current_credibility_score, state, validation/challenge/pass/seen_counts
- `trail_events`: id, deet_id, user_id, event_type, user_credibility_at_time, note_text, recipients, timestamp
- `topics`: id, name

**Active file:** `app.py` (rebuilt from scratch, ~450 lines, clean and focused)
**Port:** 8765 (0.0.0.0)

**Next (not started):**
- STEP 3: Feed UI (show deets for current user, action buttons)
- STEP 4: Trail UI (visual chain display)
- STEP 5: Teaser page (unauthenticated view of deet + install CTA)
- STEP 6: Agent seeding (simplified, no spider)

---

### Session 3: Logo Design + Agent Autonomy + Bug Fixes
- **Logo:** Designed 6 concepts, chose **Ripple Drop** (teardrop + ripple rings + center dot = viral spread mechanic). Embedded in landing + dashboard headers. Favicon ready. `LOGO_GUIDE.md` created.
- **Agent bugs fixed:**
  - Model name: Changed from dead `claude-3-5-sonnet-20241022` → `claude-opus-4-1-20250805` (working)
  - Flask watchdog: Disabled `debug=True` + reloader that caused crashes
  - Spider timeout: Skipped network scraping for now (agent uses Claude knowledge instead)
- **Agent autonomy (NEW):**
  - Added `/api/deet/<id>/accept` endpoint: Users can accept/validate deets and **auto-subscribe to topics**
  - Added `/api/user/<id>/follow/<topic>` and `/api/user/<id>/topics` endpoints for topic management
  - Agent now has dedicated user (`agent-system-001`, credibility 9.5)
  - "Validate" button now calls accept (validates + auto-follows topic)
  - Next: Auto-generation loop (agent periodically creates deets for popular topics)
- **Status:** Flask live on `localhost:5000`. Landing page, setup, dashboard, seed modal all working.

## 2026-02-21 - DotSpeak Launch: Deets System (REVISED MODEL)
- **Big Picture:** DotSpeak is the platform; Deets Dot is the launch wedge product.
- Deets Dot = credibility-scored information agent that actively pushes verified content via SMS/app.
- Goal: Single agent with "different outfits" (future: sympathy cards, group chat, dating, commerce—all same engine).
- **Launch Target:** 8-12 weeks, <$500 investment.
- **Viral Mechanic:** Share-to-view loop (friend gets SMS → taps link → sees credibility score → needs app to see full breakdown → installs → now they get deets).
- FOMO phrase: "You don't got the deets?" becomes social currency.

### Built the Deets System POC
- **Location:** `~/.openclaw/workspace/deets-system/`
- **Stack:** Flask + SQLite + Claude Haiku (agent) + Render (deploy) + Twilio (SMS).
- **Architecture:**
  - Web UI: Landing → Setup (phone, name, 1-5 topics, temperature dial) → Dashboard → Share links
  - Agent: Research topic → Score sources → Run smell test → Store → Deliver SMS
  - Database: Users, preferences, deets history, source credibility, debunked claims
  
### Full Smell-Test Logic (Built Day 1)
1. **Source Track Record:** Agent scores each source 0-10 based on historical accuracy
2. **Community Validation:** Users thumbs up/down deets → trains model
3. **Cross-Reference Count:** How many independent sources confirm
4. **Logical Consistency:** AI flags impossible timelines, contradictions
5. **Debunk History:** Checks against known false claims
6. **Sensationalism Detector:** Flags emotionally-charged language without facts

### Seed Topics for Testing
1. Celebrity/Entertainment (FOMO + credibility)
2. Sports (universal engagement)
3. Tech Breakthroughs (influencer + adult signal)
4. True Crime (highest engagement + credibility game)
5. Crypto/Finance (gamified + accuracy critical)

### Phase 1 POC (Weeks 1-3)
- [ ] Deploy to Render (free tier start, $7/mo standard later)
- [ ] You + Jim manually trigger deets for 2-3 topics
- [ ] Test full smell-test logic (verify all flags working)
- [ ] Verify SMS delivery via Twilio
- [ ] Confirm credibility scoring makes sense
- [ ] Cost: ~$10 (Haiku + Twilio)

### Phase 2 Beta (Weeks 4-6)
- [ ] Add CRON automation (daily/weekly scheduled agent runs)
- [ ] Expand to 50 beta users (family, friends, Alex's friend group)
- [ ] Polish onboarding UX
- [ ] Test share mechanic & viral loop
- [ ] Gather feedback on deet quality
- [ ] Cost: ~$50

### Phase 3 Public Launch (Weeks 7-12)
- [ ] App store submission (iOS/Android) OR PWA
- [ ] Stripe payment integration (Deets+, Deets Pro)
- [ ] Seed 5-10 viral deets on hot topics
- [ ] TikTok/Instagram campaign: "You don't got the deets?"
- [ ] Voice mode (read deet aloud)
- [ ] Cost: ~$400 total

### Pricing Tiers
- **Free:** 1 topic, daily, headline depth, 48-hour lifespan → viral fuel
- **Deets+** ($2.99/mo): 3 topics, hourly, deep research, 7-day lifespan
- **Deets Pro** ($9.99/mo): 10 topics, real-time, full credibility engine, source scorecards, historical analysis
- **Deets Business** ($29.99-99.99/mo Phase 2): White-label, custom KB, team dashboards, API

### Key Decision: Claude Haiku for Agent
- 10-15x cheaper than Sonnet
- Perfectly adequate for news summarization + credibility scoring
- Reserve Sonnet for deep research tier only (Phase 2)
- Set API spending caps: Start $50/mo, raise as revenue grows
- Cache aggressively: Same topic across users → research once, serve many

### Files Built (Phase 1 Core)
- `app.py` — Flask backend + Claude agent (research + scoring + smell test)
- `spider.py` — **POWERHOUSE WEB SCRAPER** (news, social, YouTube, articles, research)
- `templates/landing.html` — Home page
- `templates/setup.html` — Onboarding (phone, name, topics, temperature dial)
- `templates/dashboard.html` — Main interface (view deets, test topics, adjust preferences)
- `templates/share.html` — Share teaser (headline + credibility score, "Install app for full view")
- `requirements.txt` — Python deps (Flask, Anthropic, requests, BeautifulSoup, feedparser)
- `Procfile` + `render.yaml` — Render deployment config
- `gunicorn_config.py` — Gunicorn for production
- `README.md` — Full architecture + deployment guide
- `SPIDER.md` — Complete spider documentation
- `SPIDER_SETUP.md` — Spider quick start guide
- `DEPLOYMENT.md` — Deployment instructions
- `LAUNCH_CHECKLIST.md` — Testing checklist
- `START_HERE.md` — Quick orientation

### Immediate Next Steps
1. **Deploy to Render** (free → standard) — get live URL
2. **Set ANTHROPIC_API_KEY** on Render
3. **You + Jim: Create accounts** — pick 2-3 seed topics
4. **Trigger deets manually** — test agent output quality + credibility scoring
5. **Iterate smell-test logic** — refine flags based on real outputs
6. **Integrate Twilio** (optional for SMS, can test via web dashboard first)
7. **Lock launch name** — "The Deets" vs "Dot Deets"? (recommend "The Deets by DotSpeak")

### Why This Wins (vs Other DotSpeak Products)
- Single user + viral loop → no cold-start problem
- Clear credibility moat → harder to copy
- Daily habit forming → LTV compound
- Fast build speed → launch in 8-12 weeks
- Revenue clarity → freemium → natural upsell
- Fits teens + adults → dual demographic

### Future Roadmap (After Deets)
- **Spark (Cards):** One-time 2.99 greeting cards (month 4-5, requires 5K users)
- **Powwow (Groups):** Group chat coordination (month 5-7, requires 10K users)
- **Commerce Dot:** Product agent (month 6-9)
- **Dating/Match:** Personal agent matchmaking (month 8-12)
- **Agent-to-Agent:** Walgreens dream — your agent calls their agent (12+ months, needs ID infra + permissions)
