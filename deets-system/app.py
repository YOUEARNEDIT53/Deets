"""
Deets System — Phase 1 (CORE VIRAL LOOP)
Drop → Validate/Challenge → Pass → Trail
Author: Genny | Date: February 21, 2026
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import sqlite3
import json
import uuid
import logging
from anthropic import Anthropic

app = Flask(__name__)
DB_PATH = "deets_v2.db"
TOPICS = ["Celebrity/Entertainment", "Sports", "Tech Breakthroughs", "True Crime", "Crypto/Finance"]

client = Anthropic()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ DATABASE ============

def init_db():
    """Initialize database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        phone TEXT,
        credibility_score REAL DEFAULT 5.0,
        total_drops INTEGER DEFAULT 0,
        total_validations INTEGER DEFAULT 0,
        total_challenges INTEGER DEFAULT 0,
        total_passes INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Topics
    c.execute('''CREATE TABLE IF NOT EXISTS topics (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Deets (the core unit)
    c.execute('''CREATE TABLE IF NOT EXISTS deets (
        id TEXT PRIMARY KEY,
        claim_text TEXT NOT NULL,
        origin_type TEXT NOT NULL,  -- 'user', 'agent', 'anonymous'
        origin_user_id TEXT,
        topic_id TEXT NOT NULL,
        current_credibility_score REAL DEFAULT 5.0,
        state TEXT DEFAULT 'fresh',  -- fresh, spreading, hot, confirmed, debunked, faded
        validation_count INTEGER DEFAULT 0,
        challenge_count INTEGER DEFAULT 0,
        pass_count INTEGER DEFAULT 0,
        seen_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_interaction_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(origin_user_id) REFERENCES users(id),
        FOREIGN KEY(topic_id) REFERENCES topics(id)
    )''')
    
    # Trail Events (immutable history)
    c.execute('''CREATE TABLE IF NOT EXISTS trail_events (
        id TEXT PRIMARY KEY,
        deet_id TEXT NOT NULL,
        user_id TEXT,
        event_type TEXT NOT NULL,  -- drop, view, validate, challenge, pass
        user_credibility_at_time REAL,
        note_text TEXT,
        recipients TEXT,  -- JSON array for drop/pass events
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(deet_id) REFERENCES deets(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_id():
    return str(uuid.uuid4())

# ============ ROUTES ============

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        data = request.json
        user_id = generate_id()
        
        conn = get_db()
        c = conn.cursor()
        
        try:
            c.execute('''
                INSERT INTO users (id, display_name, phone)
                VALUES (?, ?, ?)
            ''', (user_id, data.get('name', 'User'), data.get('phone')))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'user_id': user_id}), 201
        except Exception as e:
            conn.close()
            return jsonify({'error': str(e)}), 400
    
    return render_template('setup.html', topics=TOPICS)

@app.route('/dashboard/<user_id>')
def dashboard(user_id):
    conn = get_db()
    c = conn.cursor()
    
    # Get user
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    if not user:
        conn.close()
        return "User not found", 404
    
    conn.close()
    return render_template('dashboard_v2.html', user=user, topics=TOPICS)

# ============ DEET ENDPOINTS ============

@app.route('/api/deet/drop', methods=['POST'])
def drop_deet():
    """User drops a deet to recipients."""
    data = request.json
    user_id = data.get('user_id')
    claim = data.get('claim', '').strip()
    topic_name = data.get('topic')
    anonymous = data.get('anonymous', False)
    recipients = data.get('recipients', [])  # list of user IDs
    
    if not claim or len(claim) > 280:
        return jsonify({'error': 'Claim required, max 280 chars'}), 400
    if not topic_name:
        return jsonify({'error': 'Topic required'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        # Validate user
        c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        if not user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Get or create topic
        c.execute('SELECT id FROM topics WHERE name = ?', (topic_name,))
        topic = c.fetchone()
        if not topic:
            topic_id = generate_id()
            c.execute('INSERT INTO topics (id, name) VALUES (?, ?)', (topic_id, topic_name))
        else:
            topic_id = topic['id']
        
        # Create deet
        deet_id = generate_id()
        initial_score = 3.0 if anonymous else 5.0
        
        c.execute('''
            INSERT INTO deets (
                id, claim_text, origin_type, origin_user_id, topic_id,
                current_credibility_score, state
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (deet_id, claim, 'user', None if anonymous else user_id, topic_id,
              initial_score, 'fresh'))
        
        # Record DROP event
        drop_event_id = generate_id()
        c.execute('''
            INSERT INTO trail_events (
                id, deet_id, user_id, event_type, user_credibility_at_time, recipients
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (drop_event_id, deet_id, None if anonymous else user_id, 'drop',
              user['credibility_score'] if not anonymous else 5.0,
              json.dumps(recipients)))
        
        # For each recipient, log VIEW event
        for recipient_id in recipients:
            view_event_id = generate_id()
            c.execute('''
                INSERT INTO trail_events (id, deet_id, user_id, event_type, user_credibility_at_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (view_event_id, deet_id, recipient_id, 'view', 5.0))
        
        # Update user drop count
        c.execute('UPDATE users SET total_drops = total_drops + 1 WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'deet_id': deet_id,
            'claim': claim,
            'score': initial_score,
            'recipients_count': len(recipients),
            'share_link': f'http://192.168.1.197:8765/deet/{deet_id}'
        }), 201
        
    except Exception as e:
        conn.rollback()
        conn.close()
        logger.error(f"Drop error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/deet/<deet_id>/validate', methods=['POST'])
def validate_deet(deet_id):
    """User validates a deet."""
    data = request.json
    user_id = data.get('user_id')
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        # Get user
        c.execute('SELECT credibility_score FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        if not user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Get deet
        c.execute('SELECT * FROM deets WHERE id = ?', (deet_id,))
        deet = c.fetchone()
        if not deet:
            conn.close()
            return jsonify({'error': 'Deet not found'}), 404
        
        # Score formula: +0.3 * (validator_credibility / 5.0)
        score_change = 0.3 * (user['credibility_score'] / 5.0)
        new_score = min(10.0, deet['current_credibility_score'] + score_change)
        
        # Update deet
        c.execute('''
            UPDATE deets SET validation_count = validation_count + 1,
                           current_credibility_score = ?,
                           last_interaction_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_score, deet_id))
        
        # Log event
        event_id = generate_id()
        c.execute('''
            INSERT INTO trail_events (id, deet_id, user_id, event_type, user_credibility_at_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (event_id, deet_id, user_id, 'validate', user['credibility_score']))
        
        # Update user
        c.execute('UPDATE users SET total_validations = total_validations + 1 WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'deet_id': deet_id,
            'new_score': new_score,
            'score_change': score_change
        }), 200
        
    except Exception as e:
        conn.rollback()
        conn.close()
        logger.error(f"Validate error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/deet/<deet_id>/challenge', methods=['POST'])
def challenge_deet(deet_id):
    """User challenges a deet."""
    data = request.json
    user_id = data.get('user_id')
    note = data.get('note', '')
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        # Get user
        c.execute('SELECT credibility_score FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        if not user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Get deet
        c.execute('SELECT * FROM deets WHERE id = ?', (deet_id,))
        deet = c.fetchone()
        if not deet:
            conn.close()
            return jsonify({'error': 'Deet not found'}), 404
        
        # Score formula: -0.3 * (challenger_credibility / 5.0)
        score_change = -0.3 * (user['credibility_score'] / 5.0)
        new_score = max(0.0, deet['current_credibility_score'] + score_change)
        
        # Update deet
        c.execute('''
            UPDATE deets SET challenge_count = challenge_count + 1,
                           current_credibility_score = ?,
                           last_interaction_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_score, deet_id))
        
        # Log event with note
        event_id = generate_id()
        c.execute('''
            INSERT INTO trail_events (id, deet_id, user_id, event_type, user_credibility_at_time, note_text)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (event_id, deet_id, user_id, 'challenge', user['credibility_score'], note))
        
        # Update user
        c.execute('UPDATE users SET total_challenges = total_challenges + 1 WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'deet_id': deet_id,
            'new_score': new_score,
            'score_change': score_change
        }), 200
        
    except Exception as e:
        conn.rollback()
        conn.close()
        logger.error(f"Challenge error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/deet/<deet_id>/pass', methods=['POST'])
def pass_deet(deet_id):
    """User passes a deet to recipients."""
    data = request.json
    user_id = data.get('user_id')
    recipients = data.get('recipients', [])
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        # Get user
        c.execute('SELECT credibility_score FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        if not user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Get deet
        c.execute('SELECT * FROM deets WHERE id = ?', (deet_id,))
        deet = c.fetchone()
        if not deet:
            conn.close()
            return jsonify({'error': 'Deet not found'}), 404
        
        # Score formula: +0.1 * (passer_credibility / 5.0) (soft validation)
        score_change = 0.1 * (user['credibility_score'] / 5.0)
        new_score = min(10.0, deet['current_credibility_score'] + score_change)
        
        # Update deet
        c.execute('''
            UPDATE deets SET pass_count = pass_count + 1,
                           current_credibility_score = ?,
                           last_interaction_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_score, deet_id))
        
        # Log PASS event with recipients
        pass_event_id = generate_id()
        c.execute('''
            INSERT INTO trail_events (id, deet_id, user_id, event_type, user_credibility_at_time, recipients)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (pass_event_id, deet_id, user_id, 'pass', user['credibility_score'],
              json.dumps(recipients)))
        
        # For each recipient, log VIEW event
        for recipient_id in recipients:
            view_event_id = generate_id()
            c.execute('''
                INSERT INTO trail_events (id, deet_id, user_id, event_type, user_credibility_at_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (view_event_id, deet_id, recipient_id, 'view', 5.0))
        
        # Update user
        c.execute('UPDATE users SET total_passes = total_passes + 1 WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'deet_id': deet_id,
            'recipients_count': len(recipients),
            'new_score': new_score
        }), 200
        
    except Exception as e:
        conn.rollback()
        conn.close()
        logger.error(f"Pass error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/deet/<deet_id>/trail', methods=['GET'])
def get_trail(deet_id):
    """Get full trail for a deet."""
    conn = get_db()
    c = conn.cursor()
    
    try:
        # Get deet
        c.execute('SELECT * FROM deets WHERE id = ?', (deet_id,))
        deet = c.fetchone()
        if not deet:
            conn.close()
            return jsonify({'error': 'Deet not found'}), 404
        
        # Get trail events
        c.execute('''
            SELECT te.*, u.display_name FROM trail_events te
            LEFT JOIN users u ON te.user_id = u.id
            WHERE te.deet_id = ?
            ORDER BY te.created_at ASC
        ''', (deet_id,))
        events = c.fetchall()
        
        trail = []
        for event in events:
            trail_item = {
                'event_type': event['event_type'],
                'user': event['display_name'] or 'Anonymous',
                'credibility': event['user_credibility_at_time'],
                'timestamp': event['created_at'],
                'note': event['note_text']
            }
            if event['recipients']:
                trail_item['recipients'] = json.loads(event['recipients'])
            trail.append(trail_item)
        
        conn.close()
        
        return jsonify({
            'deet_id': deet_id,
            'claim': deet['claim_text'],
            'current_score': deet['current_credibility_score'],
            'state': deet['state'],
            'trail': trail,
            'summary': {
                'validation_count': deet['validation_count'],
                'challenge_count': deet['challenge_count'],
                'pass_count': deet['pass_count'],
                'validation_rate': f"{int(100 * deet['validation_count'] / (deet['validation_count'] + deet['challenge_count'] + 1))}%"
            }
        }), 200
        
    except Exception as e:
        conn.close()
        logger.error(f"Trail error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/deet/<deet_id>')
def teaser_page(deet_id):
    """Public teaser page for unauthenticated users."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT * FROM deets WHERE id = ?', (deet_id,))
    deet = c.fetchone()
    conn.close()
    
    if not deet:
        return "Deet not found", 404
    
    # Teaser shows: claim, score, validation/challenge counts, install CTA
    # Does NOT show full trail or allow interaction
    return render_template('teaser.html', deet=deet)

if __name__ == '__main__':
    init_db()
    app.run(debug=False, port=5000, use_reloader=False, host='0.0.0.0', threaded=True)
