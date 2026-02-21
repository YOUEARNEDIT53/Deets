# Deets System Architecture

## System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                              │
│                                                                   │
│  [Landing]  →  [Setup]  →  [Dashboard]  →  [Share Links]       │
│   "Get the      Phone +       View deets,      Teaser view      │
│    deets"       topics         test topics      (drives app      │
│               temperature      adjust prefs     installs)        │
│               (Headlines ↔                                        │
│               Deep Research)                                      │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   Flask Backend (app.py)    │
                    │   HTTP Routing + Endpoints  │
                    └──────────────┬──────────────┘
                                   │
                 ┌─────────────────┼─────────────────┐
                 │                 │                 │
    ┌────────────▼──────────┐ ┌────▼──────┐  ┌─────▼─────────────┐
    │  SPIDER (spider.py)   │ │  Claude   │  │  DATABASE         │
    │                       │ │  Agent    │  │  (SQLite)         │
    │  Searches all sources │ │  (Haiku)  │  │                   │
    │  in parallel          │ │           │  │  Users table      │
    │                       │ │  Analyzes │  │  Preferences      │
    │  ├─ News feeds        │ │  + Scores │  │  Deets history    │
    │  │  (Reuters,         │ │  +        │  │  Source tracking  │
    │  │   AP, BBC,         │ │  Smell    │  │  Debunked claims  │
    │  │   Bloomberg, etc)  │ │  test     │  │                   │
    │  │                    │ │           │  │  (Auto-create)    │
    │  ├─ Social media      │ │  Result:  │  │                   │
    │  │  (Twitter,         │ │  JSON with│  └───────────────────┘
    │  │   Reddit,          │ │  - Headline
    │  │   TikTok,          │ │  - Summary
    │  │   Instagram)       │ │  - Sources
    │  │                    │ │  - Score 0-10
    │  ├─ YouTube           │ │  - Flags
    │  │  (trending,        │ │  - Status
    │  │   channel data)    │ │
    │  │                    │ │
    │  ├─ Articles          │ │
    │  │  (Medium,          │ │
    │  │   Substack,        │ │
    │  │   blogs)           │ │
    │  │                    │ │
    │  └─ Expert research   │ │
    │     (arXiv,           │ │
    │      Scholar,         │ │
    │      think tanks)     │ │
    │                       │ │
    │  Returns: Aggregated  │ │
    │  sources + metadata   │ │
    │  (3-8 sec, parallel)  │ │
    └───────────────────────┘ │
                               │
                 ┌─────────────▼──────────┐
                 │   Delivery Layer       │
                 │                        │
                 │  SMS via Twilio        │
                 │  (optional, Phase 2)   │
                 │                        │
                 │  Push notifications    │
                 │  (future)              │
                 │                        │
                 │  Web view sharing      │
                 │  (current)             │
                 └────────────────────────┘
```

---

## Data Flow

### User Requests a Deet

```
USER TRIGGERS TOPIC
    ↓
Flask receives request
    ↓
Extract: user_id, topic, temperature (research depth)
    ↓
Call: research_and_score(topic, temperature)
    ↓
    ├─ SPIDER.search_all(topic, temp)
    │  ├─ ThreadPoolExecutor spawns 8 concurrent searches
    │  ├─ search_news() → Reuters, AP, BBC RSS feeds
    │  ├─ search_social() → Twitter, Reddit, TikTok public data
    │  ├─ search_youtube() → YouTube search results
    │  ├─ search_articles() → Medium, Substack, blogs
    │  └─ search_analysis() → arXiv, Scholar, think tanks
    │      ↓ (all in parallel)
    │      Return: aggregated sources with metadata
    │
    └─ CLAUDE analyzes spider data
       ├─ Reads all gathered sources
       ├─ Synthesizes information
       ├─ Checks cross-references
       ├─ Runs smell test
       ├─ Assigns credibility score
       └─ Returns JSON with:
          - headline
          - summary
          - sources (with individual scores)
          - credibility_score (0-10)
          - cross_references (count)
          - smell_test_flags
          - debunk_status
    ↓
Store in database:
    - Insert into deets table
    - Update source_history (track accuracy)
    - Record metadata
    ↓
Return to user:
    - Display on dashboard
    - Ready for share
    ↓
USER INTERACTS:
    - Thumbs up/down (trains model)
    - Share link (viral loop)
    - Adjusts preferences
    - Explores other topics
```

---

## Component Breakdown

### 1. Flask Backend (app.py)

**Routes:**
- `GET /` — Landing page
- `GET/POST /setup` — Onboarding flow
- `GET /dashboard/<user_id>` — Main dashboard
- `POST /api/trigger-deet/<user_id>/<topic>` — Research & score a topic
- `POST /api/feedback/<deet_id>` — Store thumbs up/down
- `POST /api/update-preference` — Update user preferences
- `GET /share/<deet_id>` — Share teaser view

**Functions:**
- `init_db()` — Create SQLite tables
- `research_and_score()` — Main orchestration (calls spider + Claude)

### 2. Spider (spider.py)

**Class:** `DeetsSpider`

**Methods:**
- `search_all(topic, temperature)` — Parallel search all categories
- `search_news(topic)` — RSS feeds + Google News
- `search_social(topic)` — Twitter, Reddit, TikTok
- `search_youtube(topic)` — YouTube search
- `search_articles(topic)` — Medium, Substack, blogs
- `search_analysis(topic)` — arXiv, Scholar, think tanks
- `format_for_agent(spider_data)` — Format as prompt for Claude

**Performance:**
- Parallel: 8 concurrent searches via ThreadPoolExecutor
- Speed: 3-8 seconds
- Cost: ~$0.05 (API only)

### 3. Claude Agent

**Model:** claude-3-5-haiku-20241022 (cost optimized)

**Input:** Aggregated sources from spider

**Output:** JSON with credibility analysis

**What it does:**
1. Synthesizes spider data
2. Scores sources (0-10) by credibility
3. Checks cross-references
4. Runs smell test (logic, consistency, sensationalism)
5. Assigns overall credibility (0-10)
6. Returns structured output

### 4. Database (SQLite)

**Tables:**

```sql
users
├─ id (PK)
├─ phone (UNIQUE)
├─ name
└─ created_at

preferences
├─ id (PK)
├─ user_id (FK)
├─ topic
├─ temperature (0-100)
├─ frequency (daily/real-time/weekly)
├─ filters
└─ enabled

deets
├─ id (PK)
├─ user_id (FK)
├─ topic
├─ headline
├─ summary
├─ sources (JSON)
├─ credibility_score
├─ community_votes
├─ community_upvotes
├─ cross_references
├─ smell_test_flags (JSON)
├─ debunk_status
└─ created_at

source_history
├─ id (PK)
├─ source_name (UNIQUE)
├─ total_claims
├─ accurate_claims
├─ credibility_score
└─ last_updated

debunked_claims
├─ id (PK)
├─ claim_pattern (UNIQUE)
├─ debunk_reason
└─ added_date
```

### 5. Web Templates

**landing.html** — Marketing page (hook without friction)
**setup.html** — Onboarding (phone, name, topics, temperature dial)
**dashboard.html** — Main interface (deets feed, preferences, test buttons)
**share.html** — Teaser view (headline + credibility, "Install to see full")

---

## Information Flow (Detailed)

### Step 1: User Setup

```
User → Landing page (1 click) → Setup form
Setup form:
  - Phone: +1 (555) 123-4567
  - Name: Chris
  - Topics: [Sports, Tech, Crypto]
  - Temperature: 50 (Moderate research)
POST /setup → Create user + preferences → Redirect to dashboard
```

### Step 2: User Triggers Topic

```
Dashboard → Click [📡 Sports]
POST /api/trigger-deet/1/Sports
  ↓
research_and_score("Sports", 50)
  ├─ spider.search_all("Sports", 50)
  │  ├─ search_news("Sports")      → Reuters Sports, AP Sports, etc.
  │  ├─ search_social("Sports")    → #sports trending, r/sports discussions
  │  ├─ search_youtube("Sports")   → Sports highlights, analysis
  │  ├─ search_articles("Sports")  → Medium sports analysis
  │  └─ search_analysis("Sports")  → Expert commentary
  │  ↓ (all in parallel, ~8 sec total wait)
  │  Return: {
  │    'results': {
  │      'news': [...],
  │      'social': [...],
  │      'youtube': [...],
  │      'articles': [...],
  │      'analysis': [...]
  │    }
  │  }
  │
  ├─ spider.format_for_agent(spider_data)
  │  → Creates prompt with all gathered sources
  │
  └─ client.messages.create(prompt)
     → Claude analyzes all sources
     → Returns JSON with credibility score, flags, etc.
```

### Step 3: Store & Display

```
Insert into deets table:
  - user_id: 1
  - topic: Sports
  - headline: "Lakers Win Western Conference Finals"
  - summary: "Lakers defeated Celtics 4-1..."
  - sources: "[{name: 'ESPN', score: 8.5}, ...]"
  - credibility_score: 8.7
  - cross_references: 8
  - smell_test_flags: ["timeline consistent", "all sources agree"]
  - debunk_status: "confirmed"

Return to frontend:
  ← JSON response
  ← Dashboard refreshes
  ← Shows deet with score + flags + feedback buttons
```

### Step 4: User Interacts

```
User sees deet on dashboard:
  - Headline + credibility score displayed
  - Smell-test flags shown
  - Thumbs up/down buttons
  - Share button

User clicks 👍:
  POST /api/feedback/42 → {upvote: true}
  → Updates deets table: community_upvotes += 1
  → Updates source_history: ESPN credibility +0.1

User clicks 📤 (Share):
  → Generates link: /share/42
  → Friend opens link
  → Sees teaser (headline + "Credibility: 8.7/10")
  → CTA: "Download The Deets for Full Breakdown"
  → Friend installs app
  → Friend becomes user
  → Viral loop activates
```

---

## Temperature/Research Depth

**User sets temperature 0-100:**

```
0-25:    Headlines Only
├─ Spider: Quick scan (top 5 from each source)
├─ Claude: Headlines + quick summary
└─ Time: 2-3 seconds

25-75:   Moderate Research
├─ Spider: Standard depth (10 from each source)
├─ Claude: Detailed synthesis + analysis
└─ Time: 4-6 seconds

75-100:  Deep Research
├─ Spider: Deep search (all available sources)
├─ Claude: Comprehensive analysis + expert validation
└─ Time: 7-10 seconds
```

---

## Error Handling

### Spider Errors (Graceful Degradation)

```
If one source fails:
  - Continue searching others
  - Return available results
  - Log error, don't crash

If all sources fail:
  - Return empty results
  - Claude still runs (with empty sources)
  - User sees "No sources found for this topic"
```

### Claude Errors

```
If Claude returns invalid JSON:
  - Catch JSONDecodeError
  - Return error response
  - Log error
  - Don't crash app

If Claude timeout:
  - Retry once
  - If still fails, return error
  - User sees "Analysis failed, try again"
```

### Database Errors

```
If database locked (Phase 1, unlikely):
  - SQLite uses write locks
  - Only 2 users, not concurrent
  - Phase 2: Upgrade to PostgreSQL

If user not found:
  - Redirect to setup
  - Create new user
```

---

## Cost Model

### Per Search
- Spider cost: $0
- Claude Haiku: ~$0.05 (1,200 input tokens + 400 output tokens)
- **Total: ~$0.05 per deet**

### Monthly (Phase 1)
- Daily deet x 2 users x 30 days = 60 searches = $3
- Twilio (optional): $5
- Render free tier: $0
- **Total: ~$8-15/month**

### Monthly (Phase 2, 50 users)
- Daily deet x 50 users x 30 days = 1,500 searches = $75
- Twilio: $20-30
- Render Standard: $7
- **Total: ~$100-110/month**

---

## Deployment

### Local
```
python app.py
→ http://localhost:5000
```

### Render
```
1. Push to GitHub
2. Render → New Web Service
3. Connect repo
4. Set ANTHROPIC_API_KEY
5. Deploy (2-3 min)
→ https://deets-system.onrender.com
```

---

## Future Enhancements

### Phase 2
- [ ] CRON scheduler (automatic daily deets)
- [ ] Twilio SMS integration
- [ ] Source credibility learning (track accuracy over time)
- [ ] Duplicate detection
- [ ] Semantic search

### Phase 3
- [ ] Multi-language support
- [ ] Regional sources
- [ ] Image verification
- [ ] Real-time alerts
- [ ] Voice mode

### Phase 4+
- [ ] PostgreSQL (scale to 10K+ users)
- [ ] Redis caching
- [ ] GraphQL API
- [ ] Mobile app
- [ ] Commerce integration

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **SQLite** | Fast iteration, no ops burden (Phase 1). Upgrade to Postgres later. |
| **Claude Haiku** | 10-15x cheaper than Sonnet. Perfectly capable for text analysis. |
| **Parallel search** | ThreadPoolExecutor = simple, fast, scales. No complex async needed. |
| **RSS feeds** | Free, reliable, real-time updates. No auth needed. |
| **No caching (Phase 1)** | Keep simple. Add caching when scaling to 1K+ users. |
| **Freemium model** | Free tier drives installs, Premium ($2.99) drives revenue. |

---

## Security Notes

### Data Privacy
- Don't store personal user data beyond phone + name
- Anonymize social media data
- Comply with platform ToS

### API Keys
- Store in .env locally
- Store in Render env vars in production
- Never commit keys to git

### Rate Limiting
- Future: Add rate limits to API endpoints
- Current: Free tier doesn't need limits (small user count)

---

## Monitoring & Metrics

### Phase 1 (Testing)
- Monitor Render logs for errors
- Check database for stored deets
- Validate credibility scores

### Phase 2+ (Growth)
- Monitor API costs (set spending caps)
- Track credibility score accuracy
- Monitor source reliability
- Track user engagement (deets per user)
- Track viral loop (share → install conversion)

---

**This is the complete architecture. Every piece is designed for fast iteration (Phase 1) and straightforward scaling (Phase 2+).**

🏗️ Built to grow.
