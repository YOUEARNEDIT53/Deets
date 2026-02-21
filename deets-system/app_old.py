"""
Deets System — Phase 1 (REVISED MODEL)
Core: Deet creation, Trail system, Pass mechanic, Stream feed
Author: Genny (powered by Claude Sonnet 3.5)
Date: February 21, 2026
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import sqlite3
import os
import json
import uuid
from anthropic import Anthropic
# from spider import DeetsSpider  # DISABLED FOR PHASE 1 — no web scraping

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False  # Don't sort JSON keys
DB_PATH = "deets_v2.db"
TOPICS = ["Celebrity/Entertainment", "Sports", "Tech Breakthroughs", "True Crime", "Crypto/Finance"]

# Logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
client = Anthropic()
# spider = DeetsSpider()  # DISABLED FOR PHASE 1

# Try Twilio
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
twilio_client = None
if TWILIO_AVAILABLE and TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    try:
        twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except:
        pass


# ============ DATABASE INITIALIZATION ============

def init_db():
    """Create tables for REVISED deet-centric model."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users table (phone NOT unique for testing)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        display_name TEXT,
        phone TEXT,
        email TEXT,
        credibility_score REAL DEFAULT 5.0,
        total_validations INTEGER DEFAULT 0,
        total_challenges INTEGER DEFAULT 0,
        total_passes INTEGER DEFAULT 0,
        total_drops INTEGER DEFAULT 0,
        accuracy_rate REAL DEFAULT 0.5,
        subscription_tier TEXT DEFAULT 'free',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Topics table
    c.execute('''CREATE TABLE IF NOT EXISTS topics (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        category TEXT,
        subscriber_count INTEGER DEFAULT 0,
        heat_score REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Deets table (REVISED: single claim, not briefing)
    c.execute('''CREATE TABLE IF NOT EXISTS deets (
        id TEXT PRIMARY KEY,
        claim_text TEXT NOT NULL,
        origin_type TEXT NOT NULL,
        origin_user_id TEXT,
        topic_id TEXT NOT NULL,
        initial_credibility_score REAL,
        current_credibility_score REAL DEFAULT 5.0,
        state TEXT DEFAULT 'fresh',
        seen_count INTEGER DEFAULT 0,
        validation_count INTEGER DEFAULT 0,
        challenge_count INTEGER DEFAULT 0,
        pass_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_interaction_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        parent_deet_id TEXT,
        source_layer TEXT,
        FOREIGN KEY(origin_user_id) REFERENCES users(id),
        FOREIGN KEY(topic_id) REFERENCES topics(id)
    )''')
    
    # Trail Events table (REVISED: immutable log of interactions)
    c.execute('''CREATE TABLE IF NOT EXISTS trail_events (
        id TEXT PRIMARY KEY,
        deet_id TEXT NOT NULL,
        user_id TEXT,
        event_type TEXT NOT NULL,
        user_credibility_at_time REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        note_text TEXT,
        recipients TEXT,
        FOREIGN KEY(deet_id) REFERENCES deets(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # User preferences
    c.execute('''CREATE TABLE IF NOT EXISTS user_preferences (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL UNIQUE,
        topic_ids TEXT,
        temperature INTEGER DEFAULT 50,
        frequency TEXT DEFAULT 'daily',
        notification_method TEXT DEFAULT 'push',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============ HELPER FUNCTIONS ============

def generate_id():
    """Generate UUID for entities."""
    return str(uuid.uuid4())


def update_deet_state(deet_id: str, conn=None):
    """Recalculate deet state based on interactions."""
    should_close = conn is None
    if conn is None:
        conn = get_db()
    
    c = conn.cursor()
    
    # Get deet
    c.execute('SELECT * FROM deets WHERE id = ?', (deet_id,))
    deet = c.fetchone()
    
    if not deet:
        if should_close:
            conn.close()
        return
    
    validation_count = deet['validation_count']
    challenge_count = deet['challenge_count']
    total_interactions = validation_count + challenge_count
    
    # Determine state
    if deet['current_credibility_score'] < 3.0:
        new_state = 'debunked'
    elif deet['current_credibility_score'] > 8.5 and total_interactions > 1000:
        new_state = 'confirmed'
    elif validation_count > 0 and abs(validation_count - challenge_count) > 100:
        new_state = 'disputed'
    elif total_interactions > 100 and deet['current_credibility_score'] > 7.0:
        new_state = 'hot'
    elif total_interactions > 10:
        new_state = 'spreading'
    else:
        new_state = 'fresh'
    
    c.execute('UPDATE deets SET state = ? WHERE id = ?', (new_state, deet_id))
    conn.commit()
    
    if should_close:
        conn.close()


def calculate_user_credibility(user_id: str, conn=None):
    """Recalculate user credibility based on validation accuracy."""
    should_close = conn is None
    if conn is None:
        conn = get_db()
    
    c = conn.cursor()
    
    # Get all events by user
    c.execute('''
        SELECT te.id, te.event_type, d.state, d.current_credibility_score
        FROM trail_events te
        JOIN deets d ON te.deet_id = d.id
        WHERE te.user_id = ? AND te.event_type IN ('validate', 'challenge')
        ORDER BY te.timestamp
    ''', (user_id,))
    
    events = c.fetchall()
    
    correct = 0
    total = len(events)
    
    for event in events:
        # Validation correct if deet confirmed
        if event['event_type'] == 'validate' and event['state'] == 'confirmed':
            correct += 1
        # Challenge correct if deet debunked
        elif event['event_type'] == 'challenge' and event['state'] == 'debunked':
            correct += 1
    
    accuracy_rate = correct / total if total > 0 else 0.5
    credibility_score = 3.0 + (accuracy_rate * 7.0)  # 3.0-10.0 scale
    
    # Update user
    c.execute('''
        UPDATE users 
        SET credibility_score = ?, accuracy_rate = ?, total_validations = ?
        WHERE id = ?
    ''', (credibility_score, accuracy_rate, total, user_id))
    
    conn.commit()
    
    if should_close:
        conn.close()
    
    return credibility_score


# ============ ROUTES ============

@app.route('/health')
def health():
    """Health check endpoint."""
    logger.info("Health check called")
    return jsonify({'status': 'ok'}), 200

@app.route('/')
def index():
    """Landing page."""
    logger.info("Index called")
    return render_template('landing.html')


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Onboarding: topics, notification method."""
    if request.method == 'POST':
        data = request.json
        phone = data.get('phone', '')
        
        conn = get_db()
        c = conn.cursor()
        
        try:
            # Check if user already exists by phone (get_or_create pattern)
            if phone:
                c.execute('SELECT id FROM users WHERE phone = ?', (phone,))
                existing_user = c.fetchone()
                if existing_user:
                    conn.close()
                    return jsonify({'success': True, 'user_id': existing_user['id'], 'existing': True}), 200
            
            # Create new user
            user_id = generate_id()
            c.execute('''
                INSERT INTO users (id, display_name, phone)
                VALUES (?, ?, ?)
            ''', (user_id, data.get('name', 'Friend'), phone))
            
            # Create preferences
            topic_ids = json.dumps(data.get('topics', []))
            pref_id = generate_id()
            c.execute('''
                INSERT INTO user_preferences 
                (id, user_id, topic_ids, notification_method)
                VALUES (?, ?, ?, ?)
            ''', (pref_id, user_id, topic_ids, data.get('notifyMethod', 'push')))
            
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'user_id': user_id}), 201
        except Exception as e:
            conn.close()
            return jsonify({'error': str(e)}), 400
    
    return render_template('setup.html', topics=TOPICS)


@app.route('/dashboard/<user_id>')
def dashboard(user_id):
    """User dashboard: see deets, create deets, stream."""
    conn = get_db()
    c = conn.cursor()
    
    # Get user
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    if not user:
        conn.close()
        return "User not found", 404
    
    # Get deets (feed: activity-based, not chronological)
    c.execute('''
        SELECT * FROM deets
        ORDER BY last_interaction_at DESC, pass_count DESC
        LIMIT 50
    ''')
    deets = c.fetchall()
    
    conn.close()
    
    return render_template('dashboard_v2.html', user=user, deets=deets, topics=TOPICS)


# ============ DEET ENDPOINTS ============

@app.route('/api/deet/drop', methods=['POST'])
def drop_deet():
    """User drops a deet to specific recipients (the CORE mechanic)."""
    data = request.json
    user_id = data.get('user_id')
    claim = data.get('claim', '').strip()
    topic_category = data.get('topic')  # e.g., "True Crime"
    anonymous = data.get('anonymous', False)
    recipients = data.get('recipients', [])  # list of user IDs or display names
    
    if not claim or not topic_category:
        return jsonify({'error': 'Claim and topic required'}), 400
    if len(claim) > 280:
        return jsonify({'error': 'Claim max 280 characters'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        # Validate user exists
        c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        if not user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Get or create topic
        c.execute('SELECT id FROM topics WHERE name = ?', (topic_category,))
        topic_row = c.fetchone()
        if not topic_row:
            topic_id = generate_id()
            c.execute('''
                INSERT INTO topics (id, name, category)
                VALUES (?, ?, ?)
            ''', (topic_id, topic_category, 'User'))
        else:
            topic_id = topic_row['id']
        
        # Create deet
        deet_id = generate_id()
        initial_score = 3.0 if anonymous else 5.0
        
        c.execute('''
            INSERT INTO deets (
                id, claim_text, origin_type, origin_user_id, 
                topic_id, initial_credibility_score, current_credibility_score, state
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (deet_id, claim, 'user', None if anonymous else user_id, 
              topic_id, initial_score, initial_score, 'fresh'))
        
        # Record the DROP event
        drop_event_id = generate_id()
        c.execute('''
            INSERT INTO trail_events (
                id, deet_id, user_id, event_type, user_credibility_at_time, recipients
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (drop_event_id, deet_id, None if anonymous else user_id, 'drop', 
              user['credibility_score'] if not anonymous else 5.0, 
              json.dumps(recipients)))
        
        # For each recipient, log a VIEW event (they haven't seen it yet but it's in their inbox)
        for recipient_id in recipients:
            view_event_id = generate_id()
            c.execute('''
                INSERT INTO trail_events (
                    id, deet_id, user_id, event_type, user_credibility_at_time
                ) VALUES (?, ?, ?, ?, ?)
            ''', (view_event_id, deet_id, recipient_id, 'view', 5.0))
        
        # Update user's drop count
        c.execute('''
            UPDATE users SET total_drops = total_drops + 1
            WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        
        # Generate shareable link
        share_link = f"http://192.168.1.197:8765/deet/{deet_id}"
        
        return jsonify({
            'success': True,
            'deet_id': deet_id,
            'claim': claim,
            'topic': topic_category,
            'initial_score': initial_score,
            'recipients_count': len(recipients),
            'share_link': share_link
        }), 201
        
    except Exception as e:
        conn.rollback()
        conn.close()
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
    finally:
        if conn:
            conn.close()


@app.route('/api/deet/<deet_id>/validate', methods=['POST'])
def validate_deet(deet_id):
    """User validates a deet (weighted by their credibility)."""
    data = request.json
    user_id = data.get('user_id')
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        # Get user credibility
        c.execute('SELECT credibility_score FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        if not user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Get current deet score
        c.execute('SELECT current_credibility_score FROM deets WHERE id = ?', (deet_id,))
        deet = c.fetchone()
        if not deet:
            conn.close()
            return jsonify({'error': 'Deet not found'}), 404
        
        # Score formula: +0.3 * (validator_credibility / 5.0)
        score_change = 0.3 * (user['credibility_score'] / 5.0)
        new_score = min(10.0, deet['current_credibility_score'] + score_change)
        
        # Update deet
        c.execute('''
            UPDATE deets 
            SET validation_count = validation_count + 1,
                current_credibility_score = ?,
            last_interaction_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (deet_id,))
    
    # Log event
    c.execute('SELECT credibility_score FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    
    event_id = generate_id()
    c.execute('''
        INSERT INTO trail_events (
            id, deet_id, user_id, event_type, user_credibility_at_time, note_text
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (event_id, deet_id, user_id, 'validate', user['credibility_score'] if user else 5.0, note))
    
    conn.commit()
    
    # Update deet state
    update_deet_state(deet_id, conn)
    
    # Get updated deet
    c.execute('SELECT * FROM deets WHERE id = ?', (deet_id,))
    deet = c.fetchone()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'new_score': deet['current_credibility_score'],
        'validation_count': deet['validation_count'],
        'state': deet['state']
    })


@app.route('/api/deet/<deet_id>/challenge', methods=['POST'])
def challenge_deet(deet_id):
    """User challenges a deet."""
    data = request.json
    user_id = data.get('user_id')
    note = data.get('note', '')
    
    conn = get_db()
    c = conn.cursor()
    
    # Update deet
    c.execute('''
        UPDATE deets 
        SET challenge_count = challenge_count + 1,
            current_credibility_score = current_credibility_score - 0.5,
            last_interaction_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (deet_id,))
    
    # Log event
    c.execute('SELECT credibility_score FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    
    event_id = generate_id()
    c.execute('''
        INSERT INTO trail_events (
            id, deet_id, user_id, event_type, user_credibility_at_time, note_text
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (event_id, deet_id, user_id, 'challenge', user['credibility_score'] if user else 5.0, note))
    
    conn.commit()
    
    # Update deet state
    update_deet_state(deet_id, conn)
    
    # Get updated deet
    c.execute('SELECT * FROM deets WHERE id = ?', (deet_id,))
    deet = c.fetchone()
    
    # Update user credibility (if challenge later confirmed)
    calculate_user_credibility(user_id, conn)
    
    conn.close()
    
    return jsonify({
        'success': True,
        'new_score': deet['current_credibility_score'],
        'challenge_count': deet['challenge_count'],
        'state': deet['state']
    })


@app.route('/api/deet/<deet_id>/pass', methods=['POST'])
def pass_deet(deet_id):
    """User passes a deet to recipients."""
    data = request.json
    user_id = data.get('user_id')
    recipients = data.get('recipients', [])
    
    conn = get_db()
    c = conn.cursor()
    
    # Update deet
    c.execute('''
        UPDATE deets 
        SET pass_count = pass_count + 1,
            current_credibility_score = current_credibility_score + 0.2,
            last_interaction_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (deet_id,))
    
    # Log pass event
    c.execute('SELECT credibility_score FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    
    event_id = generate_id()
    c.execute('''
        INSERT INTO trail_events (
            id, deet_id, user_id, event_type, user_credibility_at_time, recipients
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (event_id, deet_id, user_id, 'pass', user['credibility_score'] if user else 5.0,
          json.dumps(recipients)))
    
    conn.commit()
    
    # Update user stats
    c.execute('''
        UPDATE users SET total_passes = total_passes + 1 WHERE id = ?
    ''', (user_id,))
    
    conn.commit()
    
    # Get updated deet
    c.execute('SELECT * FROM deets WHERE id = ?', (deet_id,))
    deet = c.fetchone()
    
    # Send SMS to user if they want to share
    c.execute('SELECT phone FROM users WHERE id = ?', (user_id,))
    user_phone = c.fetchone()
    
    if user_phone and user_phone['phone'] and twilio_client:
        try:
            # Send SMS notification that deet was passed
            message_body = f"🎯 Your deet was just passed! Score: {deet['current_credibility_score']:.1f}/10. Check your feed at http://localhost:5000"
            twilio_client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=user_phone['phone']
            )
            print(f"✅ SMS sent to {user_phone['phone']}")
        except Exception as e:
            print(f"❌ SMS failed: {e}")
    
    conn.close()
    
    return jsonify({
        'success': True,
        'deet_id': deet_id,
        'new_score': deet['current_credibility_score'],
        'pass_count': deet['pass_count'],
        'recipients_notified': len(recipients),
        'sms_sent': bool(user_phone and user_phone['phone'])
    })


@app.route('/api/feed', methods=['GET'])
def get_feed():
    """Get activity-based deet stream."""
    user_id = request.args.get('user_id')
    limit = request.args.get('limit', 20, type=int)
    
    conn = get_db()
    c = conn.cursor()
    
    # Get deets sorted by activity (hot first)
    c.execute('''
        SELECT d.*, 
            (SELECT COUNT(*) FROM trail_events WHERE deet_id = d.id) as interaction_count
        FROM deets d
        ORDER BY d.state DESC, interaction_count DESC, d.last_interaction_at DESC
        LIMIT ?
    ''', (limit,))
    
    deets = c.fetchall()
    
    # Get trail for each deet
    result = []
    for deet in deets:
        c.execute('''
            SELECT te.*, u.display_name, u.credibility_score
            FROM trail_events te
            LEFT JOIN users u ON te.user_id = u.id
            WHERE te.deet_id = ?
            ORDER BY te.timestamp DESC
            LIMIT 10
        ''', (deet['id'],))
        
        trail = c.fetchall()
        
        result.append({
            'deet': dict(deet),
            'trail': [dict(t) for t in trail],
            'state': deet['state'],
            'score': deet['current_credibility_score'],
            'interactions': deet['interaction_count']
        })
    
    conn.close()
    
    return jsonify({'deets': result})


@app.route('/api/user/<user_id>/credibility', methods=['GET'])
def get_user_credibility(user_id):
    """Get user credibility score."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''
        SELECT credibility_score, accuracy_rate, 
               total_validations, total_challenges, total_passes, total_drops
        FROM users WHERE id = ?
    ''', (user_id,))
    
    user = c.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'credibility_score': user['credibility_score'],
        'accuracy_rate': user['accuracy_rate'],
        'total_validations': user['total_validations'],
        'total_challenges': user['total_challenges'],
        'total_passes': user['total_passes'],
        'total_drops': user['total_drops']
    })


# ============ AGENT ENDPOINTS ============

def get_agent_user():
    """Get or create the agent user."""
    conn = get_db()
    c = conn.cursor()
    
    agent_id = "agent-system-001"
    c.execute('SELECT id FROM users WHERE id = ?', (agent_id,))
    if not c.fetchone():
        c.execute('''
            INSERT INTO users (id, display_name, phone, credibility_score)
            VALUES (?, ?, ?, ?)
        ''', (agent_id, 'Agent System', '+0', 9.5))
        conn.commit()
    
    conn.close()
    return agent_id

@app.route('/api/deet/seed/<topic>', methods=['POST'])
def seed_deet(topic):
    """Agent creates a deet for a topic."""
    try:
        print(f"🕷️ AGENT: Seeding deet for {topic}...")
        
        # Use Claude to create deet (skip spider for now—it hangs on network requests)
        prompt = f"""You are creating a deet about {topic}.

A deet is: ONE specific, verifiable fact. Max 280 characters. No opinion. No emoji.

Based on your knowledge, create a current/recent deet claim about {topic}.

Respond with ONLY this JSON (no markdown, no code blocks):
{{
    "claim": "One specific fact about {topic}",
    "credibility_score": 7.5,
    "sources_count": 3
}}"""
        
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1].strip()
            if response_text.startswith('json'):
                response_text = response_text[4:].strip()
        
        result = json.loads(response_text)
        
        # Create deet
        deet_id = generate_id()
        conn = get_db()
        c = conn.cursor()
        
        # Get or create topic
        c.execute('SELECT id FROM topics WHERE name = ?', (topic,))
        topic_row = c.fetchone()
        if not topic_row:
            topic_id = generate_id()
            c.execute('''
                INSERT INTO topics (id, name, category)
                VALUES (?, ?, ?)
            ''', (topic_id, topic, 'Trending'))
        else:
            topic_id = topic_row['id']
        
        initial_score = float(result.get('credibility_score', 7.0))
        claim = str(result.get('claim', f'Breaking news about {topic}'))[:280]
        
        c.execute('''
            INSERT INTO deets (
                id, claim_text, origin_type, topic_id, 
                initial_credibility_score, current_credibility_score
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (deet_id, claim, 'agent', topic_id, initial_score, initial_score))
        
        # Log agent drop
        event_id = generate_id()
        c.execute('''
            INSERT INTO trail_events (
                id, deet_id, event_type, user_credibility_at_time, note_text
            ) VALUES (?, ?, ?, ?, ?)
        ''', (event_id, deet_id, 'drop', 8.5, f"Agent-seeded from web sources"))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'deet_id': deet_id,
            'claim': claim,
            'score': initial_score
        })
        
    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")
        return jsonify({'error': 'Failed to parse response'}), 400
    except Exception as e:
        print(f"Seed error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400


# ============ SUBSCRIPTION ENDPOINTS ============

@app.route('/api/user/<user_id>/follow/<topic>', methods=['POST'])
def follow_topic(user_id, topic):
    """User subscribes to a topic."""
    conn = get_db()
    c = conn.cursor()
    
    try:
        # Get or create topic
        c.execute('SELECT id FROM topics WHERE name = ?', (topic,))
        topic_row = c.fetchone()
        if not topic_row:
            topic_id = generate_id()
            c.execute('''
                INSERT INTO topics (id, name, category)
                VALUES (?, ?, ?)
            ''', (topic_id, topic, 'User-followed'))
        else:
            topic_id = topic_row['id']
        
        # Get preferences
        c.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
        prefs = c.fetchone()
        
        if prefs:
            topic_ids = json.loads(prefs['topic_ids'])
            if topic not in topic_ids:
                topic_ids.append(topic)
                c.execute('''
                    UPDATE user_preferences SET topic_ids = ?
                    WHERE user_id = ?
                ''', (json.dumps(topic_ids), user_id))
        else:
            pref_id = generate_id()
            c.execute('''
                INSERT INTO user_preferences (id, user_id, topic_ids)
                VALUES (?, ?, ?)
            ''', (pref_id, user_id, json.dumps([topic])))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'topic': topic}), 200
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400


@app.route('/api/user/<user_id>/topics', methods=['GET'])
def get_user_topics(user_id):
    """Get topics user is following."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''
        SELECT topic_ids FROM user_preferences
        WHERE user_id = ?
    ''', (user_id,))
    
    prefs = c.fetchone()
    conn.close()
    
    topics = json.loads(prefs['topic_ids']) if prefs else []
    
    return jsonify({'topics': topics}), 200


@app.route('/api/deet/<deet_id>/accept', methods=['POST'])
def accept_deet(deet_id):
    """User accepts/validates a deet and auto-follows the topic."""
    data = request.json
    user_id = data.get('user_id')
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        # Validate the deet
        c.execute('SELECT topic_id FROM deets WHERE id = ?', (deet_id,))
        deet = c.fetchone()
        
        if not deet:
            conn.close()
            return jsonify({'error': 'Deet not found'}), 404
        
        # Get topic name
        c.execute('SELECT name FROM topics WHERE id = ?', (deet['topic_id'],))
        topic = c.fetchone()
        topic_name = topic['name'] if topic else 'Unknown'
        
        # Record validation
        event_id = generate_id()
        c.execute('''
            INSERT INTO trail_events (id, deet_id, user_id, event_type, note)
            VALUES (?, ?, ?, ?, ?)
        ''', (event_id, deet_id, user_id, 'validate', 'Accepted & following'))
        
        # Update deet
        c.execute('''
            UPDATE deets SET validation_count = validation_count + 1,
                           last_interaction_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (deet_id,))
        
        # Auto-subscribe to topic
        c.execute('SELECT topic_ids FROM user_preferences WHERE user_id = ?', (user_id,))
        prefs = c.fetchone()
        
        if prefs:
            topic_ids = json.loads(prefs['topic_ids'])
            if topic_name not in topic_ids:
                topic_ids.append(topic_name)
                c.execute('''
                    UPDATE user_preferences SET topic_ids = ?
                    WHERE user_id = ?
                ''', (json.dumps(topic_ids), user_id))
        
        # Recalculate deet state and user credibility
        update_deet_state(deet_id, conn)
        calculate_user_credibility(user_id, conn)
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'followed_topic': topic_name}), 200
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    init_db()
    # Listen on all interfaces (0.0.0.0) so it's accessible from your machine
    port = 8765  # Use 8765 instead of 5000
    print(f"Starting Flask server on 0.0.0.0:{port}...")
    app.run(debug=False, port=port, use_reloader=False, host='0.0.0.0', threaded=True)
