"""
Deets System — AI Agent for Credibility-Scored Information
Phase 1: POC with full smell-test logic + SMS delivery
Now with: POWERHOUSE WEB SPIDER + SMS via Twilio
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import sqlite3
import os
import json
from anthropic import Anthropic
from spider import DeetsSpider

# Try to import Twilio, make it optional
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

app = Flask(__name__)
DB_PATH = "deets.db"
TOPICS = ["Celebrity/Entertainment", "Sports", "Tech Breakthroughs", "True Crime", "Crypto/Finance"]

# Initialize Anthropic client
client = Anthropic()

# Initialize Spider
spider = DeetsSpider()

# Initialize Twilio (if available and configured)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

twilio_client = None
if TWILIO_AVAILABLE and TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    try:
        twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except Exception as e:
        print(f"Warning: Twilio initialization failed: {e}")

def init_db():
    """Create SQLite tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        phone TEXT UNIQUE NOT NULL,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # User preferences table
    c.execute('''CREATE TABLE IF NOT EXISTS preferences (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        topic TEXT NOT NULL,
        temperature INTEGER DEFAULT 50,
        frequency TEXT DEFAULT 'daily',
        filters TEXT,
        enabled BOOLEAN DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # Deets table (individual pieces of information)
    c.execute('''CREATE TABLE IF NOT EXISTS deets (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        topic TEXT,
        headline TEXT,
        summary TEXT,
        sources TEXT,
        credibility_score REAL,
        community_votes INTEGER DEFAULT 0,
        community_upvotes INTEGER DEFAULT 0,
        cross_references INTEGER DEFAULT 0,
        smell_test_flags TEXT,
        debunk_status TEXT,
        user_rating INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # Source credibility history table
    c.execute('''CREATE TABLE IF NOT EXISTS source_history (
        id INTEGER PRIMARY KEY,
        source_name TEXT UNIQUE NOT NULL,
        total_claims INTEGER DEFAULT 0,
        accurate_claims INTEGER DEFAULT 0,
        credibility_score REAL DEFAULT 5.0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Known debunked claims (for smell test)
    c.execute('''CREATE TABLE IF NOT EXISTS debunked_claims (
        id INTEGER PRIMARY KEY,
        claim_pattern TEXT UNIQUE NOT NULL,
        debunk_reason TEXT,
        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Landing page."""
    return render_template('landing.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """User setup: phone, name, topic selection."""
    if request.method == 'POST':
        data = request.json
        phone = data.get('phone')
        name = data.get('name')
        topics = data.get('topics', [])
        
        conn = get_db()
        c = conn.cursor()
        
        try:
            # Insert or update user
            c.execute('INSERT OR IGNORE INTO users (phone, name) VALUES (?, ?)', (phone, name))
            c.execute('SELECT id FROM users WHERE phone = ?', (phone,))
            user_id = c.fetchone()[0]
            
            # Insert topic preferences
            for topic in topics:
                c.execute('''INSERT OR IGNORE INTO preferences 
                    (user_id, topic, temperature, frequency) 
                    VALUES (?, ?, ?, ?)''', (user_id, topic, 50, 'daily'))
            
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'user_id': user_id}), 201
        except Exception as e:
            conn.close()
            return jsonify({'error': str(e)}), 400
    
    return render_template('setup.html', topics=TOPICS)

@app.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    """User dashboard: see their deets, adjust preferences."""
    conn = get_db()
    c = conn.cursor()
    
    # Get user
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    if not user:
        conn.close()
        return "User not found", 404
    
    # Get preferences
    c.execute('SELECT * FROM preferences WHERE user_id = ?', (user_id,))
    prefs = c.fetchall()
    
    # Get recent deets (last 7 days)
    c.execute('''SELECT * FROM deets WHERE user_id = ? 
        AND created_at > datetime('now', '-7 days')
        ORDER BY created_at DESC LIMIT 50''', (user_id,))
    deets = c.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', user=user, preferences=prefs, deets=deets, topics=TOPICS)

@app.route('/api/deets/<int:user_id>', methods=['GET'])
def get_deets(user_id):
    """API: Get deets for a user."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''SELECT * FROM deets WHERE user_id = ?
        ORDER BY created_at DESC LIMIT 20''', (user_id,))
    deets = c.fetchall()
    conn.close()
    
    return jsonify([dict(d) for d in deets])

@app.route('/api/update-preference', methods=['POST'])
def update_preference():
    """API: Update user preferences."""
    data = request.json
    user_id = data.get('user_id')
    topic = data.get('topic')
    temperature = data.get('temperature', 50)
    frequency = data.get('frequency', 'daily')
    
    conn = get_db()
    c = conn.cursor()
    c.execute('''UPDATE preferences 
        SET temperature = ?, frequency = ? 
        WHERE user_id = ? AND topic = ?''',
        (temperature, frequency, user_id, topic))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/feedback/<int:deet_id>', methods=['POST'])
def deet_feedback(deet_id):
    """API: Thumbs up/down on a deet (trains credibility model)."""
    data = request.json
    is_upvote = data.get('upvote', False)
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT source_name FROM deets WHERE id = ?', (deet_id,))
    result = c.fetchone()
    if not result:
        conn.close()
        return jsonify({'error': 'Deet not found'}), 404
    
    # Update deet votes
    c.execute('''UPDATE deets SET community_votes = community_votes + 1,
        community_upvotes = community_upvotes + ? WHERE id = ?''',
        (1 if is_upvote else 0, deet_id))
    
    # Update source credibility (simplified: +0.1 for upvote, -0.1 for downvote)
    # This is phase 1; will expand with historical tracking
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/share/<int:deet_id>')
def share_deet(deet_id):
    """Share view: shows teaser (headline + credibility), prompts for app install."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT * FROM deets WHERE id = ?', (deet_id,))
    deet = c.fetchone()
    
    if not deet:
        conn.close()
        return "Deet not found", 404
    
    # Calculate verification count (users who upvoted)
    c.execute('SELECT COUNT(*) as count FROM deets WHERE id = ? AND community_upvotes > 0', (deet_id,))
    verification = c.fetchone()
    verified_count = verification['count'] * 100 if verification else 0  # Mock: scale upvotes
    
    # Get topic details for breadcrumb
    topic_name = deet['topic']
    
    conn.close()
    
    return render_template('share.html', 
                         deet=deet,
                         verified_count=verified_count,
                         topic_name=topic_name)

@app.route('/api/rate-deet/<int:deet_id>', methods=['POST'])
def rate_deet(deet_id):
    """Rate a deet (1-5 stars). Trains the credibility model."""
    data = request.json
    rating = data.get('rating', 3)  # Default to 3 stars
    
    conn = get_db()
    c = conn.cursor()
    
    # Store rating (future: use this to train model)
    # For now, just log it
    c.execute('''UPDATE deets SET community_votes = community_votes + 1
        WHERE id = ?''', (deet_id,))
    
    # If rating > 3, it's positive feedback
    if rating >= 4:
        c.execute('''UPDATE deets SET community_upvotes = community_upvotes + 1
            WHERE id = ?''', (deet_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'rating': rating})

@app.route('/api/send-sms/<int:deet_id>', methods=['POST'])
def send_sms_endpoint(deet_id):
    """Send a deet via SMS to the user."""
    conn = get_db()
    c = conn.cursor()
    
    # Get deet details
    c.execute('SELECT * FROM deets WHERE id = ?', (deet_id,))
    deet_row = c.fetchone()
    
    if not deet_row:
        conn.close()
        return jsonify({'error': 'Deet not found'}), 404
    
    # Get user phone
    c.execute('SELECT phone FROM users WHERE id = ?', (deet_row['user_id'],))
    user = c.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Format deet for SMS
    deet_data = {
        'headline': deet_row['headline'],
        'credibility_score': deet_row['credibility_score'],
        'debunk_status': deet_row['debunk_status'],
        'summary': deet_row['summary']
    }
    
    # Send SMS
    success = deliver_deet_sms(user['phone'], deet_data)
    
    if success:
        return jsonify({'success': True, 'message': f'SMS sent to {user["phone"]}'})
    else:
        return jsonify({
            'success': False,
            'message': 'SMS service not configured. Configure TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER in .env',
            'preview': format_sms_message(deet_data)
        })

def research_and_score(topic: str, temperature: int) -> dict:
    """
    Claude agent: Use SPIDER to gather real-time data from all sources,
    then analyze with full credibility scoring & smell test.
    
    temperature: 0-100, where 0 = headlines only, 100 = deep research
    Returns: {
        'headline': str,
        'summary': str,
        'sources': [{'name': str, 'url': str, 'credibility': 0-10}],
        'credibility_score': 0-10,
        'cross_references': int,
        'smell_test_flags': [str],
        'debunk_status': str
    }
    """
    
    print(f"🕷️ SPIDER: Searching {topic} at depth {temperature}/100...")
    
    # STEP 1: Use SPIDER to gather real-time data from all sources
    spider_data = spider.search_all(topic, temperature=temperature)
    
    # STEP 2: Format spider results into context for Claude
    spider_context = spider.format_for_agent(spider_data)
    
    # STEP 3: Claude analyzes the gathered data
    prompt = f"""You are the Deets Agent. You have gathered real-time information from:
- Major news outlets (Reuters, BBC, Bloomberg, AP News, etc.)
- Social media (Twitter, Reddit, TikTok discussions)
- YouTube & video coverage
- Articles & analysis
- Expert research (arXiv papers, academic sources)

{spider_context}

IMPORTANT: Base your analysis ONLY on the sources provided above, not your training data.

Your job:
1. Synthesize the information from all gathered sources
2. Identify the most credible sources (major news > expert analysis > social > viral)
3. Check how many sources confirm the main claim (cross-reference count)
4. Flag any contradictions or red flags
5. Rate overall credibility 0-10 based on:
   - Source reliability (Reuters/AP = 8-9, Expert = 8, Major outlets = 7-8, Twitter/Reddit = 4-5, TikTok = 3-4)
   - How many sources agree (more agreement = higher credibility)
   - Publication recency (newer is better for fast-moving topics)
   - Expert consensus (when experts agree, confidence increases)

SMELL TEST - Flag any of these:
- Logical inconsistencies (impossible timelines, contradictions between sources)
- Unverified claims without source backing
- Sensationalism (emotionally charged language without facts)
- Bias indicators (one-sided reporting, missing context)
- Source conflicts of interest

Respond ONLY with valid JSON (no markdown, no code blocks, just raw JSON):
{{
    "headline": "Concise, factual headline (not sensationalized)",
    "summary": "2-3 sentence summary synthesizing the sources",
    "sources": [
        {{"name": "Source Name", "type": "news|social|research|analysis", "credibility_score": 7.5, "url": "link"}},
        {{"name": "Source Name", "type": "news|social|research|analysis", "credibility_score": 6.2, "url": "link"}}
    ],
    "credibility_score": 7.2,
    "cross_references": 5,
    "smell_test_flags": [
        "possible flag if found",
        "another flag",
        "timeline checks out - no red flags"
    ],
    "debunk_status": "confirmed" | "partially verified" | "unverified" | "debunked",
    "reasoning": "Brief explanation of credibility score calculation"
}}"""
    
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse JSON response
        response_text = message.content[0].text
        
        # Handle markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1].replace('json\n', '', 1)
        
        result = json.loads(response_text)
        
        # Add spider source count to result
        total_sources_found = (
            len(spider_data['results']['news']) +
            len(spider_data['results']['social']) +
            len(spider_data['results']['youtube']) +
            len(spider_data['results']['articles']) +
            len(spider_data['results']['analysis'])
        )
        result['sources_searched'] = total_sources_found
        result['spider_timestamp'] = spider_data['timestamp']
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON Parse error: {e}")
        print(f"Response was: {response_text[:200]}")
        return {
            'headline': f"Analysis failed for: {topic}",
            'summary': f"Claude returned invalid JSON. Raw response: {response_text[:100]}",
            'sources': [],
            'credibility_score': 0,
            'cross_references': 0,
            'smell_test_flags': ['error parsing response'],
            'debunk_status': 'error'
        }
    except Exception as e:
        print(f"Error researching topic: {e}")
        return {
            'headline': f"Research failed: {topic}",
            'summary': str(e),
            'sources': [],
            'credibility_score': 0,
            'cross_references': 0,
            'smell_test_flags': ['error in research'],
            'debunk_status': 'error'
        }

def deliver_deet_sms(phone: str, deet: dict) -> bool:
    """Send deet via SMS using Twilio."""
    if not twilio_client:
        print(f"[SMS MOCK] {phone}: {deet['headline']} (Credibility: {deet['credibility_score']}/10)")
        return False
    
    try:
        message = twilio_client.messages.create(
            body=format_sms_message(deet),
            from_=TWILIO_PHONE_NUMBER,
            to=phone
        )
        print(f"✅ SMS sent to {phone}: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ SMS failed for {phone}: {e}")
        return False

def format_sms_message(deet: dict) -> str:
    """Format a deet for SMS (short format)."""
    headline = deet.get('headline', 'No headline')[:80]
    score = deet.get('credibility_score', 0)
    status = deet.get('debunk_status', 'unverified')
    
    status_emoji = {
        'confirmed': '✅',
        'partially verified': '⚠️',
        'unverified': '❓',
        'debunked': '🚫'
    }.get(status, '❓')
    
    message = f"{status_emoji} {headline}\n\nCredibility: {score}/10\n\nOpen The Deets for full breakdown →"
    return message

@app.route('/api/trigger-deet/<int:user_id>/<topic>')
def trigger_deet(user_id, topic):
    """Manually trigger a deet (for testing). In production, this runs via CRON."""
    conn = get_db()
    c = conn.cursor()
    
    # Get user phone and preferences
    c.execute('SELECT phone FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    c.execute('''SELECT temperature FROM preferences WHERE user_id = ? AND topic = ?''',
        (user_id, topic))
    pref = c.fetchone()
    temperature = pref[0] if pref else 50
    
    # Research and score
    deet_data = research_and_score(topic, temperature)
    
    # Store in database
    c.execute('''INSERT INTO deets 
        (user_id, topic, headline, summary, sources, credibility_score, 
         cross_references, smell_test_flags, debunk_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (user_id, topic, deet_data['headline'], deet_data['summary'],
         json.dumps(deet_data['sources']), deet_data['credibility_score'],
         deet_data['cross_references'], json.dumps(deet_data['smell_test_flags']),
         deet_data['debunk_status']))
    
    conn.commit()
    deet_id = c.lastrowid
    conn.close()
    
    # Deliver SMS
    deliver_deet_sms(user['phone'], deet_data)
    
    return jsonify({
        'success': True,
        'deet_id': deet_id,
        'deet': deet_data
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
