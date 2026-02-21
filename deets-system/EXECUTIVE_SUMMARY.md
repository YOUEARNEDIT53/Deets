# Deets System: Executive Summary
## Original Model vs REVISED Model

**Date:** February 21, 2026  
**Decision:** What the hell changed? And do we rebuild?  
**TL;DR:** YES. The revised spec is 10x better for virality. Rebuild is 3 days. Worth it.

---

## The Shift (In One Sentence)

**Original:** "Agent researches, pushes briefing to you"  
**Revised:** "You create & pass claims, agent validates, network scores"

---

## Original Model (What We Built)

### How It Worked
1. User onboards (picks topics)
2. Agent researches topic → produces briefing (3-7 claims)
3. Agent sends briefing via SMS/push
4. User reads, rates (5-star), shares if they want
5. Friend gets link, sees teaser, installs app to see full content

### Status
✅ **Fully functional**
- Web spider (searches 8+ source types)
- Claude agent (research + scoring)
- SMS delivery (Twilio ready)
- Beautiful UI (modern design)
- Teaser pages (gates content)
- Share buttons (viral links)

### Problem
⚠️ **No real viral loop**
- Users are passive consumers ("I receive briefing")
- Sharing is optional ("I hit share button")
- No credibility incentive (my reputation doesn't matter)
- No social spread (briefing just sits in feed)
- No self-correction (anyone can say anything)

**Result:** App grows slowly. Engagement plateaus. Retention drops.

---

## REVISED Model (The New Vision)

### How It Works
1. User onboards (picks topics, notification preference)
2. User OR agent creates "deet" (single claim, 280 chars)
3. User **passes** deet to friends (active choice, credibility on line)
4. Friend receives notification: "Chris passed you a deet"
5. Friend validates/challenges/passes (trail visible)
6. Trail shows: who dropped it, who validated, scores, notes
7. Deet lives (hot, confirmed, debunked, faded) based on validations
8. Friend without app sees teaser (claim + score + social proof) but needs app to validate/pass

### Status
🔄 **In development** (3-5 days to Phase 1)
- Deet model (single claim, not briefing)
- Trail system (visible interaction chain)
- Pass mechanic (choose recipient, credibility impact)
- Deet states (fresh → spreading → hot → confirmed/debunked)
- Stream feed (activity-based, not chronological)
- User credibility (earned through accuracy)
- Agent as participant (seeds, validates, creates follow-ups)

### Why It's Better

#### Viral Loop ✅
- **Original:** Friend gets link → sees teaser → maybe installs
- **Revised:** Friend gets link → sees claim + score + "Chris validated this" → NEEDS app to validate/pass → installs → now they pass deets too

#### Social Incentives ✅
- **Original:** I share a briefing (no skin in game)
- **Revised:** I pass a deet (my credibility on the trail). If deet is confirmed, I get boost. If debunked, I take hit. So I only pass good stuff.

#### Self-Correcting ✅
- **Original:** Anyone can claim anything, briefing just spreads
- **Revised:** Deet gets validated/challenged by smart people. Score reflects reality. Debunked deets are marked.

#### Credibility Meritocracy ✅
- **Original:** Anyone's thumbs-up/down counts the same
- **Revised:** High-credibility users' validations carry more weight. System naturally filters out people who are always wrong.

#### Network Effect ✅
- **Original:** More users = more briefings (linear)
- **Revised:** More users = smarter deets = more spread = exponential

---

## The Numbers

### Original Model (Realistic)
- Share rate: 10-15% (people hit share button sometimes)
- Share-to-install: 3-5% (most people see teaser and close)
- Day 7 retention: 25% (briefing arrives, user reads, app sits dormant)
- **Monthly active users (Year 1):** 10K-50K

### Revised Model (Realistic)
- Share rate: 20%+ (people actively pass deets, credibility matters)
- Share-to-install: 10%+ (trail shows validators' credibility, compelling)
- Day 7 retention: 40%+ (user became validator, now they're invested)
- **Monthly active users (Year 1):** 100K-500K (10x growth)

---

## What Stays the Same

✅ Web spider (still finds sources)  
✅ Claude agent (updated to Sonnet, still researches)  
✅ Credibility scoring (source + claim + community)  
✅ SMS delivery (Twilio integration)  
✅ Beautiful UI (modern design, gradients, animations)  
✅ Database (SQLite, expand schema)  
✅ Teaser concept (gates full content)  

---

## What Changes

| Aspect | Original | Revised |
|--------|----------|---------|
| **Core unit** | Briefing (3-7 claims) | Deet (1 claim, 280 chars) |
| **Who creates** | Agent only | User + Agent |
| **How it spreads** | Share button (broadcast) | Pass mechanic (person-to-person) |
| **What matters** | Reading it | Validating/Passing it |
| **Your incentive** | None (passive) | Credibility score (put skin in game) |
| **Feed order** | Newest first | Activity/Hot first |
| **Visible trail** | No | Yes (entire interaction chain) |
| **Install driver** | "See content" | "Validate/pass it myself" |

---

## The Build (Phase 1: 3 Days)

### Day 1: Core Data Model
- Redesign database (deet-centric, not briefing)
- Create TrailEvent table (track interactions)
- Add user credibility tracking
- ~4-6 hours

### Day 2: Deet Lifecycle & Pass Mechanic
- Deet creation (user + agent)
- Trail system (validate/challenge/pass/ignore)
- User credibility calculation
- Pass mechanic (choose recipient, credibility impact)
- ~6-8 hours

### Day 3: Stream Feed & Testing
- Stream feed (activity-based sorting)
- Deet states (fresh → confirmed/debunked)
- Teaser page updates
- End-to-end test (create → pass → validate → trail)
- ~4-6 hours

### Phase 1 Done
- ✅ Deet creation (user + agent)
- ✅ Trail system working
- ✅ Pass mechanic operational
- ✅ Ready for Chris & Jim testing

---

## The Rebuild Cost

### Development Time
- **Phase 1:** 3 days (core engine)
- **Phase 2:** 2 weeks (network + notifications + onboarding)
- **Phase 3:** 2 weeks (payments + tiers + leaderboards)
- **Total:** 4-5 weeks to public launch

### Code Reuse
- ~60% of original code reusable (spider, agent, UI framework)
- ~40% needs rebuild (data model, feed logic, pass mechanic)

### Risk
✅ **Low**
- Core architecture (spider + agent) is solid
- New data model is straightforward
- Testing can happen immediately with Chris & Jim

---

## Why This Matters

### Original Model
- Good for "credible information delivery"
- Weak for "viral social spread"
- Competes with Apple News, Google News (they'll beat us)

### Revised Model
- Great for "credible information delivery"
- Excellent for "viral social spread"
- Unique mechanic (trail + credibility + passing)
- Competes with Twitter/Reddit but **wins on credibility**

**Bottom line:** The revised model is defensible, differentiated, and has a real viral loop.

---

## Decision Framework

### Should We Rebuild?

**YES if:**
- ✅ Viral growth matters more than quick launch
- ✅ We want defensible moat (trail + credibility system)
- ✅ We believe in credibility-as-mechanic, not just feature
- ✅ We can do Phase 1 in 3 days (we can)

**NO if:**
- ❌ We need to launch this week (we don't)
- ❌ Slow, steady growth is fine (it's not)
- ❌ We don't care about defensibility (we do)

---

## Recommendation

### Build It. Here's Why:

1. **Viral loop is 10x better**
   - Original: "Get my briefing" → optional share
   - Revised: "Pass this claim" → friend installs → friend passes → exponential

2. **Credibility mechanic is unique**
   - Your validation carries weight IF you've been right
   - Natural filter for misinformation
   - Self-correcting (no moderation needed)

3. **Timeline is tight but doable**
   - Phase 1 in 3 days
   - Phase 2 in 2 weeks
   - Live by March 10

4. **Code is mostly reusable**
   - Spider, agent, UI all stay
   - Just rebuild the model logic

5. **This is your 10x product**
   - Original is good (news delivery)
   - Revised is great (viral + credible)

---

## Next Steps

### If You Approve:
1. **Confirm Phase 1 scope** (deet creation, trail, pass mechanic)
2. **I spawn a coding agent** (Codex) to build in parallel
3. **We pair test** (you + Jim + me) on Day 3
4. **Iterate on feedback** (Day 4-5)
5. **Move to Phase 2** (topic system, notifications, beta)

### If You Want Changes:
1. **Tell me what** (specific concerns)
2. **I adjust** (spec changes, timeline updates)
3. **We proceed** (same plan)

---

## The Stakes

### Original Model
- ✅ Good, defensible product
- ✅ Competes on credibility
- ⚠️ Weak viral loop
- ⚠️ Slow growth trajectory

### Revised Model
- ✅ Great, defensible product
- ✅ Competes on credibility + virality
- ✅ Strong viral loop
- ✅ 10x growth trajectory

**Choose the version you'll be excited to show investors in 6 months.**

---

## Bottom Line

> The deet is the virus. People are the host. The app is the immune system that scores it.

**This is the vision. This is the pitch. This is why it works.**

Rebuild it right. Launch it strong. Let it spread.

---

**Your call, Chris.** 🎯

- **Approve Phase 1 rebuild:** Say the word, I start now
- **Want to discuss:** Call me, we talk
- **Want modifications:** Tell me, I adjust

Either way, we're building the right product. Question is just: how fast do we want to move?

🔥
