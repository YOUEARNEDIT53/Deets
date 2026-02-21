# Deets System — Phase 1 Launch Checklist

## Pre-Launch (Now)

- [x] Build Flask app skeleton + database schema
- [x] Build Claude agent (research + credibility scoring + smell test)
- [x] Build web UI (landing, setup, dashboard, share)
- [x] Write deployment guide
- [x] Create requirements.txt + Render config
- [ ] **YOU DO NOW:** Test locally
  - [ ] Run `python app.py` locally
  - [ ] Visit http://localhost:5000
  - [ ] Create account (test phone)
  - [ ] Pick 2-3 topics
  - [ ] Click topic button
  - [ ] Verify agent runs + returns credibility score
  - [ ] Check all smell-test flags appear

## Deploy to Render

- [ ] Push code to GitHub
- [ ] Create Render service (follow DEPLOYMENT.md)
- [ ] Set ANTHROPIC_API_KEY env var
- [ ] Wait for deploy to finish
- [ ] Visit live URL
- [ ] Create account on live service
- [ ] Test topic trigger on production
- [ ] Verify logs show no errors

## Phase 1 Testing (You + Jim)

### Week 1: Core Loop

- [ ] **You:** Create account (your phone, pick 3 topics)
- [ ] **You:** Trigger deets on each topic (manually, via button)
- [ ] **You:** Verify credibility scores make sense (0-10, feels calibrated)
- [ ] **You:** Check smell-test flags (do they catch issues?)
- [ ] **You:** Thumbs up/down a few deets (verify feedback stores)
- [ ] **You:** Share a deet (verify teaser link works)

- [ ] **Jim:** Create account (his phone, pick 3 different topics)
- [ ] **Jim:** Trigger deets on his topics
- [ ] **Jim:** Same verification steps as you

### Week 2: Quality Iteration

- [ ] Review agent output quality
  - [ ] Headlines: clear and concise?
  - [ ] Summaries: factually accurate (you validate)?
  - [ ] Credibility scores: do they match reality?
  - [ ] Smell-test flags: are they useful or noisy?
- [ ] Adjust agent prompt if needed
  - [ ] Improve headline generation?
  - [ ] Refine smell-test logic?
  - [ ] Add/remove source types?
- [ ] Re-test with revised agent

### Week 3: Seed Topics Deep Dive

Test all 5 seed topics thoroughly:

1. **Celebrity/Entertainment**
   - [ ] Research current Oscar predictions or movie releases
   - [ ] Verify sources (Variety, Hollywood Reporter, etc. score high)
   - [ ] Check credibility score is 7-8 range (subjective topic, some uncertainty)

2. **Sports**
   - [ ] Pick current sport (Super Bowl, March Madness, etc.)
   - [ ] Verify agent finds recent games/trades
   - [ ] Check credibility score high (sports facts are verifiable)

3. **Tech Breakthroughs**
   - [ ] Pick recent AI release or product launch
   - [ ] Verify sources (The Verge, Wired, arXiv, company blog)
   - [ ] Check credibility scores reflect source reliability

4. **True Crime**
   - [ ] Pick active case or recent development
   - [ ] Verify agent cross-references properly (multiple outlets confirm)
   - [ ] Check smell-test flags speculation vs. facts

5. **Crypto/Finance**
   - [ ] Pick crypto price movement or SEC news
   - [ ] Verify agent captures multiple perspectives (bullish/bearish)
   - [ ] Check sensationalism detection works (volatility news often hype)

## Smell-Test Logic Verification

Each deet should show:
- [ ] **Source Track Record** (e.g., "CNN: 7.2/10, Reuters: 8.5/10")
- [ ] **Cross-references** (e.g., "Confirmed by 4 sources")
- [ ] **Logical Consistency Flags** (e.g., "Timeline checks out")
- [ ] **Debunk Status** ("unverified" / "partially verified" / "confirmed" / "debunked")
- [ ] **Sensationalism Check** (flag if exaggerated)

If any missing: update agent prompt in `app.py`

## Feedback Loops

- [ ] Thumbs up increases that source's credibility slightly
- [ ] Thumbs down decreases credibility slightly
- [ ] After 10-20 deets, verify source scores are updating
- [ ] Check database (open deets.db in SQLite viewer):
  - `SELECT * FROM source_history;` — sources updating?
  - `SELECT * FROM deets ORDER BY created_at DESC LIMIT 5;` — recent deets stored?

## SMS Delivery (Optional for POC)

If you want SMS:
- [ ] Get Twilio account
- [ ] Add TWILIO_* env vars to Render
- [ ] Uncomment SMS code in `deliver_deet_sms()`
- [ ] Test: trigger deet, verify SMS arrives
- Cost: ~$5-10/mo for light testing

For now, web dashboard is fine for testing. Skip SMS until Phase 2.

## Next Phase Prep

Once Phase 1 is solid:
- [ ] **Jim:** Identify 5 hot launch topics (what would Alex's friend group care about?)
- [ ] **You:** Design CRON schedule (daily 9 AM? Real-time?)
- [ ] **Both:** Lock the product name ("The Deets" vs "Dot Deets"? vs other?)
- [ ] **You:** Plan Phase 2 onboarding UX polish
- [ ] **You:** Plan share mechanic (how does teaser link work?)

## Launch Readiness Criteria

**SHIP Phase 1 when:**

✅ Agent produces high-quality deets consistently  
✅ Credibility scoring makes sense to both of you  
✅ Smell-test logic catches obvious red flags  
✅ Web UI is intuitive (setup → dashboard → trigger → result)  
✅ No crashes or errors after 20+ topic triggers  
✅ Feedback loops storing data correctly  
✅ You're both using it daily and finding value  

**If any of these aren't true:** iterate that week, don't move forward

## After Phase 1 Passes

→ **Phase 2 Begin:** CRON automation, 50-user beta, onboarding polish  
→ **Timeline:** Week 4-6  
→ **Deliverable:** Daily deets sent to 50 beta users automatically

---

## Debugging Commands

### If something breaks locally:

```bash
# Stop Flask
Ctrl+C

# Check database
sqlite3 deets.db
SELECT COUNT(*) FROM deets;
SELECT * FROM users;

# Clear database (start fresh)
rm deets.db

# Reinstall deps
pip install -r requirements.txt --upgrade

# Run with verbose logging
FLASK_DEBUG=1 python app.py
```

### If something breaks on Render:

- Go to Render dashboard
- Click **Logs** tab
- Look for error messages
- Check **Environment** vars are set
- Restart service (click **Restart** button)

---

## Key Questions to Answer This Week

1. **Agent Quality:** Does it actually find relevant, accurate information?
2. **Credibility Scoring:** Do the scores match your intuition (is CNN really higher credibility than random Twitter account)?
3. **Smell Test:** Are the flags useful or just noise?
4. **Naming:** Do you like "The Deets" or should we change it?
5. **Topics:** Are these 5 the right launch seeds or should we pivot?
6. **Frequency:** Should Phase 2 be daily, real-time, or user-configurable?

Discuss with Jim after Week 1 testing.

---

**Status:** Ready to launch  
**Your move:** Push to GitHub + deploy to Render  
**Next checkpoint:** Phase 1 testing complete (3 weeks)
