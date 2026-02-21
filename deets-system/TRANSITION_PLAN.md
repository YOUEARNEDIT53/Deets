# Deets System: Original → Revised Transition Plan

**Date:** February 21, 2026  
**Status:** Major Pivot - Rebuilding Core Model  
**Timeline:** 3-5 days to Phase 1 complete

---

## What We Had (Original Model)

### Core Unit: Briefing
- Agent researches topic
- Produces 3-7 claims with credibility scores
- Delivers as SMS/push notification
- User rates briefing (5-star)
- User shares briefing link

**Status:** ✅ Fully functional (spider + agent + SMS + ratings + share)

### User Experience
1. Onboarding (topics, temperature, frequency)
2. Receive briefing notification
3. Open briefing, see multiple claims
4. Rate, share, or dismiss
5. Receive next briefing per schedule

**Status:** ✅ Landing page, setup flow, dashboard, ratings, SMS all working

---

## What We're Building (Revised Model)

### Core Unit: Deet (Single Claim)
- User creates deet (280 chars, single claim)
- OR agent seeds deet (from multiple sources)
- Deet spreads through "passing" (active, personal)
- Trail shows entire journey (who touched it, when, credibility impact)
- Deet lives (hot/confirmed/debunked/faded)
- Credibility changes based on validations/challenges

**Status:** 🔄 In development

### User Experience
1. Onboarding (topics, notification preference)
2. See stream of live deets (activity-based)
3. Deets dropped to you specifically (personal section)
4. Catch & react: ✅ Validate, ❌ Challenge, ➡️ Pass, ⏭️ Ignore
5. Pass deet to contacts (put credibility on line)
6. Trail shows who validated/challenged + their scores
7. Deet lives in stream or archives (depends on state)

---

## Keep vs Rebuild

### Keep ✅ (Still Valid)
| Component | Reuse |
|-----------|-------|
| Web spider | ✅ YES - finds sources |
| Claude agent | ✅ YES - updated to Sonnet, still does research |
| Credibility scoring (3-level) | ✅ YES - source + claim + community |
| SMS delivery | ✅ YES - send deet to contacts |
| Beautiful UI | ✅ YES - redesign for new model |
| Teaser page concept | ✅ YES - gates full trail |
| Database (SQLite) | ✅ YES - expand schema |

### Rebuild 🔄 (New Model)

| Component | Reason |
|-----------|--------|
| **Deet model** | Was: briefing (collection). Now: claim (single) |
| **Trail system** | Was: none. Now: visible interaction chain |
| **Pass mechanic** | Was: share button. Now: active, personal, credible |
| **Feed layout** | Was: briefing cards. Now: deet stream (activity-based) |
| **User credibility** | Was: vote weight. Now: full score based on accuracy |
| **Deet states** | Was: none. Now: fresh/spreading/hot/confirmed/debunked |
| **Agent role** | Was: primary creator. Now: participant (seeds, validates) |
| **Onboarding** | Was: topics/temp/freq/notify. Now: simplified (topics/notify) |

---

## Build Plan (Phase 1 - 3 Days)

### Day 1: Core Data Model
- [ ] Update database schema (deet-centric)
  - Deet table (claim, origin, state, scores)
  - TrailEvent table (interactions)
  - User credibility tracking
  - Topic table
- [ ] Update app.py to use new schema
- [ ] Test data creation

### Day 2: Deet Lifecycle
- [ ] Create deet endpoint (user creates)
- [ ] Agent creates deets (from web sources)
- [ ] Implement states (fresh → confirmed/debunked)
- [ ] Implement trail events (validate/challenge/pass/ignore)
- [ ] Update user credibility scores based on outcomes

### Day 3: Pass Mechanic & Stream
- [ ] Implement pass mechanic (select recipient, credibility impact)
- [ ] Build stream feed (activity-based sorting)
- [ ] Teaser page for deet links (gates trail)
- [ ] Pass-outside-app flow (text link, teaser, install)
- [ ] Test end-to-end deet creation → passing → trail

### End of Day 3: Phase 1 Complete
- Deet creation (user + agent)
- Trail system (interactions tracked)
- Pass mechanic (person-to-person)
- Stream feed (activity-based)
- Ready for Chris & Jim testing

---

## What Stays the Same (User-Facing)

✅ **App still looks modern** (gradients, animations, beautiful UI)  
✅ **Still uses SMS** (Twilio delivery)  
✅ **Still has credibility scores** (0-10)  
✅ **Still has web search** (spider + agent)  
✅ **Still mobile-first** (responsive, clean)  

---

## What Changes (User-Facing)

| Feature | Original | Revised |
|---------|----------|---------|
| **Core unit** | Briefing (3-7 claims) | Deet (1 claim, 280 chars) |
| **Creation** | Agent only | User + agent |
| **Delivery** | Push/SMS notification | Personal "drop" or public stream |
| **Interaction** | Rate briefing (5-star) | Validate/Challenge/Pass/Ignore |
| **Feed** | Chronological (newest first) | Activity-based (hottest now) |
| **Trail** | None | Visible chain (who touched, when) |
| **Spread** | Share button (broadcast) | Pass mechanic (choose recipient) |
| **State** | Implicit (read/unread) | Explicit (fresh/hot/confirmed/debunked) |

---

## Model Update: Haiku → Sonnet

**Why:** Claude Haiku (deprecated Feb 19, 2026) → Claude Sonnet 3.5

**What changed in code:**
```python
# OLD
model="claude-3-5-haiku-20241022"

# NEW  
model="claude-3-5-sonnet-20241022"
```

**Impact:**
- ✅ Better research quality (Sonnet > Haiku)
- ✅ Better reasoning for deet creation
- ✅ Better smell-test logic
- ⚠️ Slightly higher cost (but still <$0.10 per deet)

---

## Testing Strategy

### Phase 1 Testing (Chris & Jim)
1. **Create deets:**
   - Chris drops deet about topic X
   - Agent auto-creates deet from web sources (topic Y)
   - Verify claims are <280 chars
   
2. **Trail system:**
   - Chris drops deet to Jim
   - Jim validates it
   - Chris opens same deet, sees Jim's validation on trail
   - Jim's credibility weighted correctly
   
3. **Pass mechanic:**
   - Jim passes deet to 2 other people
   - Each person's reaction updates trail
   - Score reflects aggregate validation
   
4. **Stream feed:**
   - Chris and Jim see live deets in activity order
   - Newly dropped deets appear
   - Hot deets (many interactions) prominent
   - Fading deets dim appropriately

### Success Criteria
- Deet creation works (user + agent)
- Trail system tracks interactions correctly
- Pass mechanic weights credibility properly
- Stream shows right deets at right time
- No crashes, no data loss

---

## Schema Changes (Database)

### Remove
```sql
-- Old briefing model
DROP TABLE deets;  -- will be reimplemented
DROP TABLE sources;  -- merge into deet
```

### Create
```sql
-- New deet-centric model
CREATE TABLE deets (
  id UUID PRIMARY KEY,
  claim_text VARCHAR(280) NOT NULL,
  origin_type ENUM ('user', 'agent', 'anonymous'),
  origin_user_id UUID NULLABLE,
  topic_id UUID NOT NULL,
  initial_score FLOAT,
  current_score FLOAT,
  state ENUM ('fresh', 'spreading', 'hot', 'confirmed', 'disputed', 'debunked', 'faded'),
  seen_count INT DEFAULT 0,
  validation_count INT DEFAULT 0,
  challenge_count INT DEFAULT 0,
  pass_count INT DEFAULT 0,
  created_at TIMESTAMP,
  last_interaction_at TIMESTAMP,
  parent_deet_id UUID NULLABLE,
  source_layer JSON
);

CREATE TABLE trail_events (
  id UUID PRIMARY KEY,
  deet_id UUID NOT NULL,
  user_id UUID NULLABLE,
  event_type ENUM ('drop', 'validate', 'challenge', 'pass', 'ignore', 'view'),
  user_credibility_at_time FLOAT,
  timestamp TIMESTAMP,
  note TEXT,
  recipients JSON  -- for pass events
);

ALTER TABLE users ADD COLUMN credibility_score FLOAT DEFAULT 5.0;
ALTER TABLE users ADD COLUMN accuracy_rate FLOAT DEFAULT 0.5;
ALTER TABLE users ADD COLUMN total_validations INT DEFAULT 0;
ALTER TABLE users ADD COLUMN total_challenges INT DEFAULT 0;
ALTER TABLE users ADD COLUMN total_passes INT DEFAULT 0;
ALTER TABLE users ADD COLUMN total_drops INT DEFAULT 0;
```

---

## API Changes

### New Endpoints

```
POST /api/deet/create
{
  "claim_text": "The Epstein files show...",
  "topic_id": "uuid",
  "origin_type": "user|agent|anonymous",
  "recipient_type": "person|group|public",
  "recipients": ["user_id_1", "user_id_2"]  // for person/group
}
Response: { deet_id, initial_score, trail: [] }

POST /api/deet/{deet_id}/validate
{ "note": "optional explanation" }
Response: { success, new_score, user_credibility_update }

POST /api/deet/{deet_id}/challenge
{ "note": "why you challenge this" }
Response: { success, new_score, user_credibility_update }

POST /api/deet/{deet_id}/pass
{
  "recipient_type": "person|group|public",
  "recipients": ["user_id_1"]
}
Response: { success, notification_sent, trail_updated }

GET /api/feed
{ topics: ["topic_id_1"], sort: "activity" }
Response: [
  {
    deet: { ... },
    trail: [ { event_type, user, credibility, timestamp } ],
    current_score: 7.8
  }
]

GET /api/user/{user_id}/credibility
Response: {
  credibility_score: 7.2,
  accuracy_rate: 0.82,
  total_validations: 45,
  total_challenges: 8,
  total_passes: 120,
  total_drops: 12
}
```

### Removed Endpoints
```
POST /api/trigger-deet (manual briefing)
POST /api/rate-deet (5-star rating)
POST /api/feedback (thumbs up/down)
```

---

## Timeline

### Day 1 (Now) ✅
- [x] Read revised spec
- [x] Update model (Haiku → Sonnet)
- [x] Create transition plan

### Day 2-3 (Tomorrow)
- [ ] Update database schema
- [ ] Implement deet creation (user + agent)
- [ ] Implement trail system
- [ ] Implement pass mechanic
- [ ] Build stream feed

### Day 4 (Friday)
- [ ] Test with Chris & Jim
- [ ] Iterate based on feedback
- [ ] Prepare for 50-user beta

### Week 2
- [ ] Phase 2: Topic system, notifications, onboarding
- [ ] 50-user beta launch

---

## Key Insight

The original model was good, but the **revised model is better for virality**.

### Original
"I get a briefing pushed to me" → "I read it, maybe share it" → Engagement stops

### Revised
"I create a claim" → "I pass it to friends" → "My credibility is on the line" → "Friends validate/challenge/pass" → "Trail shows journey" → "New people install to see it" → **Viral loop**

**The deet is the virus. People are the host. The app is the immune system.**

This model has:
- ✅ Social spread (active passing, not passive sharing)
- ✅ Credibility incentives (your score changes based on accuracy)
- ✅ Self-correcting (debunked deets marked, validators/challengers weighted)
- ✅ Meritocracy (accuracy = influence)
- ✅ Viral install loop (need app to see full trail)

---

## Next: Spawn Coding Agent

Once you confirm Phase 1 scope, I can spawn a **Codex/Claude Code agent** to rebuild the core in parallel with me.

This keeps momentum while ensuring quality.

**Ready?** 🚀
