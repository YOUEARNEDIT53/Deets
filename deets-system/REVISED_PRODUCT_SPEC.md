# Deets Product Spec - REVISED
## The Social Spreading Mechanic

**Status:** Major Pivot - Building New MVP  
**Date:** February 21, 2026  
**Model Updated:** Claude Haiku → Claude Sonnet 3.5

---

## What Changed (vs Original Spec)

### Original Model
- **Core Unit:** Briefing (collection of claims)
- **Delivery:** Agent pushes to user via notification/SMS
- **Interaction:** User rates briefing
- **Spread:** Share button on briefing

### REVISED Model
- **Core Unit:** Deet (single claim, 280 char max)
- **Delivery:** User creates & drops deet; agent seeds topics; deets spread via "passes"
- **Interaction:** Validate / Challenge / Pass / Ignore
- **Spread:** Active pass mechanic (choose recipient, put credibility on line)
- **Trail:** Visible chain showing entire journey (who dropped, passed, validated, challenged)
- **States:** Fresh → Spreading → Hot → Confirmed/Disputed/Debunked/Faded

---

## Core Concept: The Deet

A **deet** is not a notification, article, or post. It's a **living piece of information**.

### Anatomy of a Deet
```
THE CLAIM
"The Epstein flight logs show 37 visits by [name]."
[Single, specific, verifiable/debunkable]

THE ORIGIN
Dropped by: Chris (credibility 7.2) | Anonymous | Agent-sourced

THE SCORE
Current: 8.7/10 (updates in real-time)
Starts at: 5.0 (user) | 3.0 (anonymous) | 7.0+ (agent-sourced)

THE TRAIL
Seen by 4,312 • Passed by 891 • 94% validated
[Complete chain of interactions: Who → What → When]

THE LIFESPAN
Born → Spreads → Hot → Confirmed/Debunked/Faded
[Active while people interact, dims when abandoned]
```

---

## The Trail: The Killer Feature

The **trail** is a visible chain of everyone who touched the deet.

### What the Trail Shows
- **Headline bar:** Claim + score + "Seen by 4,312 • Passed by 891 • 94% validated"
- **Chain:** Dropped by [X] → Passed by [Y] (8.2) → Validated by [Z] (7.9) → Passed to you
- **Validation breakdown:** 412 validated (green bar) | 23 challenged (red) | 3,877 viewed (gray)
- **Source layer:** "7 news sources confirm. Highest credibility: AP News (8.9/10)"
- **Challenges:** If anyone challenged with a note, show it: "Marcus (8.2): Timeline doesn't match"

### Why This Matters
Unlike Twitter (replies sorted by engagement) or Reddit (upvotes by popularity), the trail:
- Shows credibility of people who validated/challenged
- Makes you accountable (your validation/pass goes on the permanent record)
- Creates meritocracy (accurate validators build credibility, wrong ones are filtered)
- Self-corrects (if you validate something later debunked, your score drops)

---

## The Life of a Deet (Step-by-Step)

### Step 1: Birth
A deet is born one of three ways:
1. **User creates it:** "+" button → type claim (280 char) → choose recipient → drop
2. **Agent creates it:** Finds claim across multiple sources, auto-generates deet
3. **External link:** Person without app gets link, clicks it, brings deet into network

Initial score:
- User-created: 5.0/10 (unverified)
- Anonymous: 3.0/10 (unverified + anonymous)
- Agent-sourced: 7.0-9.0/10 (pre-validated against sources)

### Step 2: First Pass
Creator drops it to:
- **Specific person:** "Chris dropped you a deet"
- **Group:** Everyone gets it simultaneously
- **Public stream:** Anyone following topic can see it
- **Outside app:** Generate link, send via SMS/WhatsApp/etc

### Step 3: Catch & React
Recipient opens deet, sees:
- The claim
- Current score
- Trail so far
- Four options (one tap each):

| Action | Effect |
|--------|--------|
| ✅ Validate | "I believe this." Score UP (weighted by validator's credibility) |
| ❌ Challenge | "This seems wrong." Score DOWN + optional note |
| ➡️ Pass | Send to contacts. Small score boost (soft validation) |
| ⏭️ Ignore | No action. "Seen" count +1, no "pass" = soft negative |

### Step 4: Cascade
Each person who passes spreads it to their contacts. Deet moves through network. Each interaction updates score in real-time.

Key difference from Twitter: **Deet is moving between people, not sitting in a feed.**

### Step 5: Critical Mass or Death
- **Confirmed:** 1,000+ interactions, score >8.5 → Green check, archived as reference
- **Disputed:** ~50/50 split validation/challenge → Yellow warning, agent researches
- **Debunked:** Score <3.0 → Red X, dimmed in feeds
- **Faded:** No interactions 48+ hours → Archived, no longer in active stream

---

## Deet States & Lifecycle

| State | When | Visual | Behavior |
|-------|------|--------|----------|
| **Fresh** | Just created, <10 interactions | Pulsing indicator, score "Early" | High visibility to get reactions |
| **Spreading** | 10-100 interactions, actively passed | Warm glow, trail growing | In topic streams, agent researches |
| **Hot** | 100+ interactions, score >7.0 | Fire indicator, "Trending" | Surfaced widely, agent creates follow-ups |
| **Confirmed** | 1,000+ interactions, score >8.5 | Green check | Reference material, linked to future deets |
| **Disputed** | Split opinion, ~50/50 | Yellow warning | Agent searches for more sources |
| **Debunked** | Score <3.0, majority challenged | Red X | Still visible but marked, credibility adjustments |
| **Faded** | No interactions 48+ hours | Grayed out | Archived, searchable, no longer active |

---

## The Pass Mechanic

**Passing ≠ Sharing**

- **Sharing:** Passive (hit button, appears on wall, broadcast)
- **Passing:** Active, personal (choose recipient, put your name/credibility on trail)

### How Passing Works
- **Pass to person:** Select contact, deet arrives as notification, your name on trail
- **Pass to group:** Multiple contacts get it simultaneously
- **Pass public:** Enter public stream with your name on trail
- **Pass outside app:** Generate link, send via SMS/WhatsApp/etc

### Why Passing Has Weight
When you pass a deet:
- Your name goes on the trail permanently
- If deet is later Confirmed, you get credibility boost (you helped spread truth)
- If deet is later Debunked, you take credibility hit (you spread misinformation)
- Natural incentive: only pass things you believe are credible

**This is the self-regulating mechanism that prevents misinformation.**

---

## The Feed: A Stream, Not a Wall

### What It Looks Like
The home screen is a **river of deets**, not a wall of posts.
- **Hot ones:** Bright, big, moving slower so you can catch them
- **Cold ones:** Dim, small, rushing past
- **Personal drops:** Pinned at top (people specifically sent to you)
- **Public stream:** Below personal deliveries, activity-based

### How It's Organized
**By activity, NOT chronology.**
- A deet created days ago but currently being passed → top
- A fresh deet with no traction → sinks fast
- Shows what's ALIVE NOW, not what's newest

### Personal Deliveries
When someone passes you a deet, it appears in separate section: "Deets dropped for you"
- Doesn't disappear until you interact (validate, challenge, pass, dismiss)
- Feels personal, like someone tapping your shoulder

---

## User Credibility System

Every user has a **credibility score** (0-10, visible on profile)

### How It Changes
| Action | Effect |
|--------|--------|
| Validate deet → Confirmed | Score UP |
| Challenge deet → Debunked | Score UP |
| Validate deet → Debunked | Score DOWN |
| Challenge deet → Confirmed | Score DOWN |
| Pass deet → Confirmed | Small boost |
| Pass deet → Debunked | Small hit |
| Drop deet → Confirmed | Significant boost |
| Drop deet → Debunked | Significant hit |

### What It Means
- **High credibility (7+):** Your validations move the needle more, your challenges carry weight
- **Top 1%:** Get visual badge, become trusted validators
- **Gamification:** People WANT to be right because it builds their score

---

## The Agent's Role

Agent is a **participant in network**, NOT primary content creator.

### Agent's Jobs
1. **Seed hot topics:** Trending across sources → agent drops deet into public stream
2. **Back-check in real-time:** User-created deet gaining traction → agent runs source research
3. **Smell-test deets:** Flag logical inconsistencies (timeline errors, impossible facts)
4. **Create follow-ups:** New info changes picture → "Update: [original deet] adjusted to [new score]"
5. **Deliver digests:** For daily/weekly users, compile hottest deets per topic (each carries trail)

---

## The Install Loop

How deets spread and drive app growth:

1. **Alex gets app** from Chris
2. **Chris drops her a deet** about trending topic
3. **Alex validates & passes to 7 friends**
   - Friends WITH app: get notification, open, react
   - Friends WITHOUT app: get text link
4. **Friends without app see teaser:**
   - ✅ Claim, score ("8.7/10"), social proof ("341 validated, including Alex")
   - ❌ Full trail, validation details, ability to validate, dig deeper
   - CTA: "Get the deets — free"
5. **Some install app**
   - Taken directly to deet with full trail visible
   - Prompted to pick topic, set preferences
   - Start getting their own deets
6. **New users pass deets to THEIR friends**
   - Cycle repeats

**Key:** Teaser shows enough to WANT it, but not enough to NOT need it.

---

## The Teaser Page (Revised)

When someone without app taps deet link:

### VISIBLE on Teaser
- The claim in full
- Credibility score (e.g., 8.7/10)
- "341 validated • 12 challenged"
- "Passed by 89 people including [friend name]"
- "7 news sources confirm this"
- Current state ("Hot" with fire indicator)
- "Your friend Alex passed this to you"

### GATED Behind App Install
- The trail — who dropped, passed, validated
- WHO validated/challenged + their credibility scores
- Challenge notes — WHY people disagree
- Full chain — how it got from origin to you
- WHICH sources + individual credibility scores
- Ability to validate, challenge, or pass yourself
- Alex's credibility score and validation history

**Design rule:** "Outside a party looking through window. Can see/hear something exciting. Can't dance until install."

---

## New Data Model

### DEET
```
{
  id: UUID,
  claim_text: string (max 280 chars),
  origin_type: enum [user | agent | anonymous],
  origin_user_id: UUID (nullable),
  topic_category: string,
  initial_credibility_score: float (0-10),
  current_credibility_score: float (0-10),
  state: enum [fresh | spreading | hot | confirmed | disputed | debunked | faded],
  seen_count: int,
  validation_count: int,
  challenge_count: int,
  pass_count: int,
  created_timestamp: datetime,
  last_interaction_timestamp: datetime,
  parent_deet_id: UUID (for follow-ups),
  source_layer: { sources, confirmations, contradictions }
}
```

### TRAIL_EVENT
```
{
  id: UUID,
  deet_id: UUID,
  user_id: UUID (nullable if anonymous),
  event_type: enum [drop | validate | challenge | pass | ignore | view],
  timestamp: datetime,
  note_text: string (for challenges with explanation),
  user_credibility_score_at_time: float,
  recipients: [UUID] (for pass events)
}
```

### USER
```
{
  id: UUID,
  display_name_or_alias: string,
  phone: string (optional),
  email: string (optional),
  credibility_score: float (0-10),
  total_validations: int,
  total_challenges: int,
  total_passes: int,
  total_drops: int,
  accuracy_rate: float (confirmed_validations / total_validations),
  subscription_tier: enum [free | deets_plus | deets_pro],
  topic_subscriptions: [UUID],
  temperature_setting: int (0-100),
  frequency_setting: enum [real-time | daily | weekly],
  delivery_preference: enum [push | sms | both],
  content_filters: { exclude_categories, block_sources },
  created_date: datetime,
  last_active_date: datetime
}
```

### TOPIC
```
{
  id: UUID,
  name: string,
  category: string,
  subscriber_count: int,
  heat_score: float (based on active deet count + interaction velocity),
  created_date: datetime
}
```

---

## MVP Scope (Revised)

### Phase 1: The Engine (Week 1-3)
- [ ] Deet creation (user + agent)
- [ ] Trail system (visible interaction chain)
- [ ] Validate/Challenge/Pass/Ignore actions
- [ ] Deet states (fresh → spreading → hot → confirmed/debunked)
- [ ] User credibility calculation
- [ ] Pass outside app (link + teaser)
- [ ] Agent seeding (monitors sources, auto-creates deets)
- Test with Chris & Jim for 1 week

### Phase 2: The Network (Week 4-6)
- [ ] Topic system (subscribe, discover)
- [ ] Stream feed (activity-based, not chronological)
- [ ] Notifications (push/SMS for personal drops & hot deets)
- [ ] Teaser page (drives installs)
- [ ] Onboarding (4 screens)
- [ ] 50-user beta launch
- [ ] Track: share rate, install rate, retention

### Phase 3: The Money (Week 7-12)
- [ ] Tier gating (Free/Deets+/Deets Pro)
- [ ] Payment flow (Stripe)
- [ ] Credibility leaderboard
- [ ] Digest delivery system
- [ ] Public app store launch

---

## Success Metrics

### Phase 1
- Agent produces high-quality deets consistently
- Credibility scoring makes intuitive sense
- Smell-test flags catch real issues
- Trail system works (interactions store correctly)

### Phase 2
- **Share rate:** 20%+ of users pass ≥1 deet/week
- **Share-to-install:** 10%+ of link taps install app
- **Day 7 retention:** 40%+ open briefing after 7 days
- **Trail accuracy:** Interactions correctly weighted by credibility

### Phase 3
- **Free-to-paid conversion:** 5-8% within 30 days
- **Monthly recurring revenue:** Tracking
- **Network effect:** More users → better credibility scoring

---

## What This Means

### Original Model (Still Valid)
- Web spider for gathering sources ✅
- Claude agent for research & scoring ✅
- Credibility engine (3 levels) ✅
- SMS delivery ✅

### New Model (Major Changes)
- **Deets, not briefings** — Single claims spread through network
- **Trails, not notifications** — Visible chain shows journey
- **Pass mechanic, not share button** — Active, personal, credible
- **Stream feed, not chronological** — Activity-based, alive now
- **User credibility** — Earned through accuracy, not purchased
- **Agent as participant** — Seeds topics, back-checks, creates follow-ups

### The Shift
From: "Agent researches, pushes to users"  
To: "Users create & pass deets, agent seeds & validates, network spreads"

**The deet is the virus. People are the host. The app is the immune system that scores it.**

---

## Build Priority

1. ✅ Web spider (already built)
2. ✅ Claude agent (needs model update to Sonnet) ← DONE
3. 🔄 Deet model (claim + trail system)
4. 🔄 User credibility calculation
5. 🔄 Pass mechanic (active, not share)
6. 🔄 Deet states (fresh → confirmed/debunked)
7. 🔄 Teaser page (gates full trail)
8. 🔄 Stream feed (activity-based)
9. 🔄 Topic subscriptions
10. 🔄 Notification system

---

## Next Steps

1. **Update database schema** (deet-centric, trail events)
2. **Create deet creation flow** (user + agent)
3. **Implement trail system** (interaction logging)
4. **Build pass mechanic** (choose recipient, credibility impact)
5. **Test with Chris & Jim** (drop deets to each other)

The engine is proven. The model is clear. Let's rebuild it the right way.

🔥 **The deet is the virus. Light the fire. Let it spread.**
