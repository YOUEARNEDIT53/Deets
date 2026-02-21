"""
Jupiter FL Home Finder — Chris Bolender
2BR/1BA | ~1,200 sqft | ≤$800k | Near parks/water | Good neighborhood
"""
from flask import Flask, render_template_string, request, jsonify, redirect
import sqlite3, os, json, requests
from datetime import datetime
from xml.etree import ElementTree as ET
import html as htmllib

app = Flask(__name__)
DB = os.path.join(os.path.dirname(__file__), 'homes.db')
UPLOAD = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD, exist_ok=True)

# ── DB Setup ──────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS saved_homes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT, price INTEGER, beds INTEGER, baths REAL,
        sqft INTEGER, source TEXT, url TEXT, image_url TEXT,
        notes TEXT DEFAULT '', starred INTEGER DEFAULT 0,
        status TEXT DEFAULT 'new', added_date TEXT,
        lat REAL, lng REAL, walk_score INTEGER, park_score INTEGER,
        water_dist TEXT, neighborhood_score INTEGER
    );
    CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT, results_count INTEGER, date TEXT
    );
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        home_id INTEGER, note TEXT, date TEXT
    );
    """)
    conn.commit()
    conn.close()

init_db()

# ── Helpers ───────────────────────────────────────────────
SEARCH_PARAMS = {
    'city': 'Jupiter, FL',
    'budget': 800000,
    'beds_min': 2,
    'baths_min': 1,
    'sqft_min': 1000,
    'sqft_max': 1500,
    'lat': 26.9342,
    'lng': -80.0942
}

def build_source_urls():
    """Pre-built deep-link search URLs for all major platforms"""
    return {
        'Zillow': {
            'url': 'https://www.zillow.com/jupiter-fl/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22mapBounds%22%3A%7B%22west%22%3A-80.18%2C%22east%22%3A-80.04%2C%22south%22%3A26.89%2C%22north%22%3A26.98%7D%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A800000%7D%2C%22beds%22%3A%7B%22min%22%3A2%7D%2C%22baths%22%3A%7B%22min%22%3A1%7D%2C%22sqft%22%3A%7B%22min%22%3A1000%2C%22max%22%3A1500%7D%7D%7D',
            'color': '#006AFF',
            'icon': '🏠'
        },
        'Redfin': {
            'url': 'https://www.redfin.com/city/9029/FL/Jupiter/filter/min-beds=2,min-baths=1,max-price=800000,min-sqft=1000,max-sqft=1500',
            'color': '#e8191a',
            'icon': '🔴'
        },
        'Realtor.com': {
            'url': 'https://www.realtor.com/realestateandhomes-search/Jupiter_FL/beds-2/baths-1/price-na-800000/sqft-1000-1500',
            'color': '#cc0000',
            'icon': '🏡'
        },
        'Homes.com': {
            'url': 'https://www.homes.com/jupiter-fl/2-bedrooms/1-bathrooms/?maxPrice=800000',
            'color': '#6c5ce7',
            'icon': '🌴'
        },
        'Trulia': {
            'url': 'https://www.trulia.com/FL/Jupiter/#lp=800000&beds=2&baths=1&sqft=1000:1500',
            'color': '#53b374',
            'icon': '🔎'
        },
    }

def get_walk_score(address):
    """Try Walk Score API (free tier, no key needed for basic)"""
    try:
        r = requests.get(
            'https://api.walkscore.com/score',
            params={'format':'json','address':address,'lat':SEARCH_PARAMS['lat'],'lon':SEARCH_PARAMS['lng'],'wsapikey':'your_key_here'},
            timeout=5
        )
        if r.status_code == 200:
            d = r.json()
            return d.get('walkscore', 0)
    except:
        pass
    return None

JUPITER_NEIGHBORHOODS = [
    {'name':'Abacoa','desc':'Master-planned community, walkable town center, parks, A-rated schools','park_score':9,'water':0.5,'vibe':'Family-friendly, lively','avg_price':550000,'score':92},
    {'name':'Admirals Cove','desc':'Gated waterfront, deep-water dockage, golf, ultra-luxury','park_score':7,'water':0.1,'vibe':'Ultra-luxury, boating lifestyle','avg_price':2800000,'score':60},
    {'name':'Jupiter Farms','desc':'Acreage lots, equestrian, rural feel, great for space lovers','park_score':6,'water':2.0,'vibe':'Rural, quiet, acreage','avg_price':650000,'score':72},
    {'name':'Pennock Point','desc':'Old Jupiter charm, waterfront, historic character','park_score':7,'water':0.2,'vibe':'Historic, waterfront','avg_price':900000,'score':78},
    {'name':'River Place','desc':'Intracoastal access, quiet streets, very close to beach','park_score':8,'water':0.3,'vibe':'Waterfront, residential','avg_price':850000,'score':80},
    {'name':'Mallory Creek','desc':'New construction, community pool, near Abacoa, good schools','park_score':8,'water':1.5,'vibe':'New, family, community','avg_price':620000,'score':85},
    {'name':'Botanica','desc':'Gated, lush landscaping, townhomes, close to I-95','park_score':7,'water':1.8,'vibe':'Quiet, gated','avg_price':480000,'score':83},
    {'name':'Island Country Club','desc':'Golf course community, affordable relative to Jupiter','park_score':7,'water':1.0,'vibe':'Golf, residential','avg_price':380000,'score':79},
    {'name':'Tequesta','desc':'Adjacent to Jupiter, small-town feel, waterfront access','park_score':8,'water':0.4,'vibe':'Quaint, waterfront, artsy','avg_price':520000,'score':88},
    {'name':'Limestone Creek','desc':'Quiet neighborhood, good value, near I-95','park_score':6,'water':2.5,'vibe':'Value, residential','avg_price':430000,'score':75},
]

NEARBY_PARKS = [
    {'name':'Carlin Park','type':'Beach/Picnic','desc':'Beach access, tennis, picnic pavilions, dog beach','dist':'1.2 mi to beach','rating':'⭐⭐⭐⭐⭐'},
    {'name':'DuBois Park','type':'Beach/Swimming','desc':'Hidden gem — stunning snorkeling, calm water, historic DuBois House','dist':'2 mi from downtown','rating':'⭐⭐⭐⭐⭐'},
    {'name':'Jupiter Ridge Natural Area','type':'Nature/Hiking','desc':'Scrub habitat, birding, 5 miles of trails','dist':'Near central Jupiter','rating':'⭐⭐⭐⭐'},
    {'name':'Riverbend Park','type':'River/Kayak','desc':'Loxahatchee River access, kayak launch, camping, manatees','dist':'West Jupiter','rating':'⭐⭐⭐⭐⭐'},
    {'name':'Roger Dean Chevrolet Stadium','type':'Sports','desc':'Spring training — Cardinals & Marlins, minor league games','dist':'Abacoa area','rating':'⭐⭐⭐⭐'},
    {'name':'Loggerhead Marinelife Center','type':'Wildlife','desc':'Sea turtle rescue and rehab, free admission, beach walks','dist':'Juno Beach (5 mi)','rating':'⭐⭐⭐⭐⭐'},
    {'name':'Jonathan Dickinson State Park','type':'State Park','desc':'Largest state park in SE Florida — kayaking, manatees, camping','dist':'Hobe Sound (10 mi)','rating':'⭐⭐⭐⭐⭐'},
    {'name':'Jupiter Beach Park','type':'Beach','desc':'Public beach, parking, lifeguards, great for swimming','dist':'Jupiter Island area','rating':'⭐⭐⭐⭐'},
]

WATER_HIGHLIGHTS = [
    '🌊 Jupiter Inlet — 2 miles from downtown. World-class fishing, surfing, snorkeling',
    '🚣 Loxahatchee River — Only wild & scenic river in FL. Kayaking, manatees, otters',
    '🌴 Intracoastal Waterway — Runs through Jupiter. Waterfront dining, marinas',
    '🐠 Gulf Stream — Just offshore. Warm water = great diving/fishing year-round',
    '🦈 Jupiter Reef — Renowned diving, shark diving, tropical fish',
    '🛥️ Jupiter Inlet Lighthouse — Iconic landmark, lighthouse beach, amazing views',
]

MARKET_STATS = {
    'median_price': 685000,
    'price_per_sqft': 485,
    'avg_days_on_market': 32,
    'inventory': 'Low',
    'trend': '+4.2% YoY',
    'best_months': 'Jan–Mar (snowbird season, more inventory)',
    'tip': 'Cash offers preferred. Pre-approval essential. Move fast — good homes under $800k go in days.'
}

# ── ROUTES ────────────────────────────────────────────────
@app.route('/')
def index():
    conn = get_db()
    saved = conn.execute("SELECT * FROM saved_homes ORDER BY starred DESC, added_date DESC").fetchall()
    conn.close()
    sources = build_source_urls()
    top5 = sorted(JUPITER_NEIGHBORHOODS, key=lambda x: x['score'], reverse=True)[:5]
    starred = len([h for h in saved if h['starred']])
    return render_template_string(TEMPLATE,
        saved=saved, sources=sources,
        neighborhoods=JUPITER_NEIGHBORHOODS,
        top5_neighborhoods=top5,
        starred_count=starred,
        parks=NEARBY_PARKS,
        water=WATER_HIGHLIGHTS,
        market=MARKET_STATS,
        params=SEARCH_PARAMS,
        magazine_links=MAGAZINE_LINKS,
        community_links=COMMUNITY_LINKS,
        tab=request.args.get('tab','dashboard')
    )

@app.route('/add_home', methods=['POST'])
def add_home():
    d = request.json or request.form
    conn = get_db()
    conn.execute("""
        INSERT INTO saved_homes (address,price,beds,baths,sqft,source,url,image_url,notes,status,added_date)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        d.get('address',''), int(d.get('price',0)), int(d.get('beds',2)),
        float(d.get('baths',1)), int(d.get('sqft',0)),
        d.get('source','Manual'), d.get('url',''), d.get('image_url',''),
        d.get('notes',''), 'new', datetime.now().strftime('%Y-%m-%d')
    ))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/update_home/<int:hid>', methods=['POST'])
def update_home(hid):
    d = request.json or request.form
    conn = get_db()
    for key in ['notes','status','starred']:
        if key in d:
            conn.execute(f"UPDATE saved_homes SET {key}=? WHERE id=?", (d[key], hid))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/delete_home/<int:hid>', methods=['POST'])
def delete_home(hid):
    conn = get_db()
    conn.execute("DELETE FROM saved_homes WHERE id=?", (hid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/star/<int:hid>', methods=['POST'])
def star(hid):
    conn = get_db()
    cur = conn.execute("SELECT starred FROM saved_homes WHERE id=?", (hid,)).fetchone()
    new_val = 0 if cur and cur['starred'] else 1
    conn.execute("UPDATE saved_homes SET starred=? WHERE id=?", (new_val, hid))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'starred': new_val})

@app.route('/api/stats')
def stats():
    conn = get_db()
    saved = conn.execute("SELECT COUNT(*) as c FROM saved_homes").fetchone()['c']
    starred = conn.execute("SELECT COUNT(*) as c FROM saved_homes WHERE starred=1").fetchone()['c']
    conn.close()
    return jsonify({'saved': saved, 'starred': starred})

# ── TEMPLATE ──────────────────────────────────────────────
TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>🌴 Jupiter Home Finder</title>
<style>
:root{--bg:#0f1117;--s1:#181b27;--s2:#1e2235;--s3:#262a3a;--bdr:#2a2e42;--txt:#e2e4eb;--dim:#6b7280;
--acc:#4f8ff7;--grn:#34d399;--yel:#fbbf24;--red:#f87171;--pur:#a78bfa;--cyn:#22d3ee;--ora:#fb923c;
--font:'Inter',system-ui,sans-serif}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:var(--font);background:var(--bg);color:var(--txt);min-height:100vh;font-size:20px}
::-webkit-scrollbar{width:6px;height:6px}::-webkit-scrollbar-thumb{background:var(--s3);border-radius:3px}
.hdr{background:linear-gradient(135deg,#0f2040,#1a3060);border-bottom:1px solid var(--bdr);padding:14px 24px;
  display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100}
.hdr-left{display:flex;align-items:center;gap:12px}
.hdr-logo{font-size:32px}.hdr-t{font-size:28px;font-weight:700}.hdr-sub{font-size:17px;color:var(--dim)}
.criteria{display:flex;gap:8px;flex-wrap:wrap}
.ctag{background:rgba(79,143,247,.15);border:1px solid rgba(79,143,247,.3);border-radius:12px;
  padding:5px 12px;font-size:13px;font-weight:600;color:var(--acc)}
.nav{display:flex;gap:3px;padding:8px 20px;background:var(--s1);border-bottom:1px solid var(--bdr);overflow-x:auto}
.nb{background:none;border:none;color:var(--dim);font-size:18px;font-weight:500;padding:7px 14px;
  border-radius:7px;cursor:pointer;white-space:nowrap;transition:all .15s}
.nb:hover{background:var(--s2);color:var(--txt)}.nb.a{background:var(--acc);color:#fff}
.main{max-width:1300px;margin:0 auto;padding:20px}
.kg{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:18px}
.kpi{background:var(--s1);border:1px solid var(--bdr);border-radius:10px;padding:14px;position:relative;overflow:hidden}
.kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:3px}
.kpi.bl::before{background:var(--acc)}.kpi.gr::before{background:var(--grn)}.kpi.ye::before{background:var(--yel)}
.kpi.re::before{background:var(--red)}.kpi.pu::before{background:var(--pur)}.kpi.cy::before{background:var(--cyn)}
.kl{font-size:15px;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;font-weight:600}
.kv{font-size:34px;font-weight:700;margin:4px 0 2px}.kd{font-size:15px;color:var(--dim)}
.cd{background:var(--s1);border:1px solid var(--bdr);border-radius:10px;margin-bottom:14px}
.ch{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid var(--bdr);background:var(--s2)}
.ct{font-size:20px;font-weight:600}.cb{padding:16px}
.btn{padding:6px 14px;border-radius:7px;border:1px solid var(--bdr);background:var(--s2);color:var(--txt);
  cursor:pointer;font-size:14px;font-weight:500;transition:all .15s;display:inline-flex;align-items:center;gap:5px}
.btn:hover{background:var(--s3);border-color:var(--acc)}.btn-p{background:var(--acc);border-color:var(--acc);color:#fff}
.btn-p:hover{background:#3a6bc5}.btn-red{border-color:var(--red);color:var(--red)}.btn-red:hover{background:rgba(248,113,113,.1)}
.source-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.source-card{border:1px solid var(--bdr);border-radius:10px;padding:16px;text-align:center;
  background:var(--s2);transition:all .2s;cursor:pointer;text-decoration:none;display:block}
.source-card:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,.3);border-color:var(--acc)}
.source-icon{font-size:44px;margin-bottom:8px}.source-name{font-size:20px;font-weight:700;margin-bottom:4px}
.source-desc{font-size:16px;color:var(--dim)}
.nbh-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.nbh-card{border:1px solid var(--bdr);border-radius:10px;padding:14px;background:var(--s2);position:relative}
.nbh-score{position:absolute;top:12px;right:12px;width:48px;height:48px;border-radius:50%;display:flex;
  align-items:center;justify-content:center;font-weight:700;font-size:20px}
.score-hi{background:rgba(52,211,153,.2);color:var(--grn);border:2px solid var(--grn)}
.score-mid{background:rgba(251,191,36,.2);color:var(--yel);border:2px solid var(--yel)}
.nbh-name{font-weight:700;font-size:21px;margin-bottom:4px}.nbh-desc{font-size:16px;color:var(--dim);margin-bottom:8px}
.nbh-tags{display:flex;gap:4px;flex-wrap:wrap}
.ntag{font-size:15px;padding:2px 7px;border-radius:10px;font-weight:500}
.ntag-pk{background:rgba(52,211,153,.15);color:var(--grn)}.ntag-wt{background:rgba(34,211,238,.15);color:var(--cyn)}
.ntag-pr{background:rgba(167,139,250,.15);color:var(--pur)}
.home-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}
.home-card{border:1px solid var(--bdr);border-radius:12px;background:var(--s2);overflow:hidden;
  transition:all .2s;position:relative}
.home-card:hover{transform:translateY(-3px);box-shadow:0 12px 32px rgba(0,0,0,.4)}
.home-img{width:100%;height:180px;background:linear-gradient(135deg,var(--s3),var(--s2));
  display:flex;align-items:center;justify-content:center;font-size:48px;position:relative}
.home-img img{width:100%;height:100%;object-fit:cover}
.home-star{position:absolute;top:10px;right:10px;font-size:20px;cursor:pointer;transition:transform .2s}
.home-star:hover{transform:scale(1.3)}
.home-body{padding:14px}
.home-price{font-size:30px;font-weight:700;color:var(--grn);margin-bottom:4px}
.home-addr{font-size:18px;color:var(--dim);margin-bottom:8px}
.home-specs{display:flex;gap:12px;font-size:18px;font-weight:600;margin-bottom:10px}
.home-spec{display:flex;align-items:center;gap:4px}
.home-source{font-size:15px;color:var(--dim);padding:2px 8px;border:1px solid var(--bdr);border-radius:10px}
.status-badge{font-size:15px;font-weight:600;padding:2px 8px;border-radius:10px}
.status-new{background:rgba(79,143,247,.2);color:var(--acc)}
.status-touring{background:rgba(251,191,36,.2);color:var(--yel)}
.status-offer{background:rgba(167,139,250,.2);color:var(--pur)}
.status-pass{background:rgba(107,114,128,.2);color:var(--dim)}
.park-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px}
.park-card{border:1px solid var(--bdr);border-radius:8px;padding:12px;background:var(--s2)}
.park-type{font-size:16px;color:var(--cyn);font-weight:600;text-transform:uppercase;margin-bottom:4px}
.park-name{font-weight:700;font-size:19px;margin-bottom:4px}.park-desc{font-size:16px;color:var(--dim)}
.water-list{display:flex;flex-direction:column;gap:8px}
.water-item{padding:14px 18px;background:var(--s2);border-radius:8px;border-left:3px solid var(--cyn);font-size:18px}
.market-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}
.market-stat{background:var(--s2);border:1px solid var(--bdr);border-radius:8px;padding:12px;text-align:center}
.market-val{font-size:30px;font-weight:700;color:var(--yel);margin:4px 0}
.market-label{font-size:15px;color:var(--dim);text-transform:uppercase}
.tip-box{background:rgba(79,143,247,.08);border:1px solid rgba(79,143,247,.2);border-radius:8px;
  padding:12px 16px;font-size:12px;margin-top:12px}
.add-form{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.form-full{grid-column:1/-1}
input,select,textarea{background:var(--s2);border:1px solid var(--bdr);color:var(--txt);
  padding:10px 14px;border-radius:7px;width:100%;font-size:15px;font-family:var(--font)}
input:focus,select:focus,textarea:focus{outline:1px solid var(--acc)}
label{font-size:17px;color:var(--dim);margin-bottom:4px;display:block}
.form-group{display:flex;flex-direction:column}
.empty-state{text-align:center;padding:40px;color:var(--dim)}
.empty-state .big{font-size:48px;margin-bottom:12px}.empty-state p{font-size:20px}
table{width:100%;border-collapse:collapse;font-size:12px}
th{text-align:left;color:var(--dim);font-weight:600;font-size:16px;text-transform:uppercase;letter-spacing:.4px;
  padding:7px 10px;border-bottom:1px solid var(--bdr);background:var(--s1)}
td{padding:8px 10px;border-bottom:1px solid var(--bdr);vertical-align:middle}
tr:hover td{background:rgba(79,143,247,.03)}
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:500;align-items:center;justify-content:center}
.modal-overlay.open{display:flex}
.modal{background:var(--s1);border:1px solid var(--bdr);border-radius:14px;padding:24px;width:90%;max-width:560px;max-height:90vh;overflow-y:auto}
.modal h3{font-size:16px;margin-bottom:16px}
.criteria-bar{background:var(--s2);border:1px solid var(--bdr);border-radius:10px;padding:12px 16px;
  margin-bottom:16px;display:flex;gap:16px;flex-wrap:wrap;align-items:center}
.crit-item{display:flex;flex-direction:column;gap:2px}
.crit-label{font-size:16px;color:var(--dim);text-transform:uppercase}
.crit-value{font-size:24px;font-weight:700;color:var(--acc)}
</style>
</head>
<body>

<div class="hdr">
  <div style="background:rgba(52,211,153,.12);border:1px solid rgba(52,211,153,.3);border-radius:10px;padding:8px 14px;text-align:center;font-size:15px;margin-bottom:8px">
    📱 <b>Share with wife:</b> &nbsp;<a href="http://192.168.1.197:8765/favorites" style="color:#34d399;font-weight:700" target="_blank">192.168.1.197:8765/favorites</a>
    &nbsp;&nbsp;|&nbsp;&nbsp; Full dashboard: <a href="http://192.168.1.197:8765" style="color:#4f8ff7" target="_blank">192.168.1.197:8765</a>
  </div>
  <div class="hdr-left">
    <span class="hdr-logo">🌴</span>
    <div>
      <div class="hdr-t">Jupiter Home Finder</div>
      <div class="hdr-sub">Chris Bolender • Jupiter, FL • Personal Search Dashboard</div>
    </div>
  </div>
  <div class="criteria">
    <span class="ctag">🛏 2 bed / 1 bath</span>
    <span class="ctag">📐 ~1,200 sqft</span>
    <span class="ctag">💰 ≤ $800k</span>
    <span class="ctag">🌊 Near water</span>
    <span class="ctag">🌳 Parks nearby</span>
  </div>
  </div>
</div>

<div class="nav" id="nav">
  {% set tabs = [('dashboard','📊 Dashboard'),('search','🔍 Search'),('saved','❤️ Saved ('+saved|length|string+')'),('neighborhoods','🏘 Neighborhoods'),('parks','🌳 Parks & Water'),('market','📈 Market Intel'),('magazines','📰 Magazines & Posts'),('add','➕ Add Home')] %}
  {% for tid, tlabel in tabs %}
    <button class="nb {% if tab==tid %}a{% endif %}" onclick="goTab('{{tid}}')">{{tlabel}}</button>
  {% endfor %}
</div>

<div class="main">

<!-- ═══ DASHBOARD ═══ -->
<div id="tab-dashboard" {% if tab!='dashboard' %}style="display:none"{% endif %}>
  <div class="kg">
    <div class="kpi bl"><div class="kl">Saved Homes</div><div class="kv">{{saved|length}}</div><div class="kd">in your list</div></div>
    <div class="kpi gr"><div class="kl">Starred</div><div class="kv">{{starred_count}}</div><div class="kd">top picks</div></div>
    <div class="kpi ye"><div class="kl">Budget</div><div class="kv">$800k</div><div class="kd">max purchase price</div></div>
    <div class="kpi cy"><div class="kl">Target Size</div><div class="kv">~1,200</div><div class="kd">sqft (1,000–1,500)</div></div>
    <div class="kpi pu"><div class="kl">Search Area</div><div class="kv">Jupiter</div><div class="kd">Palm Beach County, FL</div></div>
    <div class="kpi re"><div class="kl">Market</div><div class="kv">$685k</div><div class="kd">median price, +4.2% YoY</div></div>
  </div>

  <div class="cd">
    <div class="ch"><span class="ct">🏠 What You're Looking For</span></div>
    <div class="cb">
      <div class="criteria-bar">
        <div class="crit-item"><div class="crit-label">Type</div><div class="crit-value">2BR / 1BA</div></div>
        <div class="crit-item"><div class="crit-label">Size</div><div class="crit-value">~1,200 sqft</div></div>
        <div class="crit-item"><div class="crit-label">Max Price</div><div class="crit-value">$800,000</div></div>
        <div class="crit-item"><div class="crit-label">Location</div><div class="crit-value">Jupiter, FL</div></div>
        <div class="crit-item"><div class="crit-label">Must Have</div><div class="crit-value">Parks + Water</div></div>
        <div class="crit-item"><div class="crit-label">Price/sqft</div><div class="crit-value">~$667</div></div>
      </div>
      <p style="font-size:18px;color:var(--dim);margin-bottom:10px">Jupiter FL is one of the best towns in South Florida — Roger Dean Stadium, DuBois Park, Jupiter Inlet, walkable Abacoa. You're looking in the right place.</p>
      <div style="background:rgba(52,211,153,.08);border:1px solid rgba(52,211,153,.2);border-radius:8px;padding:12px;font-size:12px">
        🎯 <b>Best bets:</b> Abacoa, Tequesta, Mallory Creek, Botanica — all hit your criteria on price, walkability, parks, and neighborhood quality.
      </div>
    </div>
  </div>

  {% if saved %}
  <div class="cd">
    <div class="ch"><span class="ct">❤️ Recent Saved Homes</span><a href="?tab=saved" style="color:var(--acc);font-size:11px;text-decoration:none">View all →</a></div>
    <div class="cb">
      <div class="home-grid">
        {% for h in saved[:3] %}
        <div class="home-card">
          <div class="home-img">🏠
            <span class="home-star" onclick="toggleStar({{h.id}}, this)">{{' ⭐' if h.starred else ' 🤍'}}</span>
          </div>
          <div class="home-body">
            <div class="home-price">${{'{:,}'.format(h.price)}}</div>
            <div class="home-addr">{{h.address}}</div>
            <div class="home-specs">
              <span class="home-spec">🛏 {{h.beds}}bd</span>
              <span class="home-spec">🛁 {{h.baths}}ba</span>
              <span class="home-spec">📐 {{'{:,}'.format(h.sqft)}} sqft</span>
            </div>
            <div style="display:flex;gap:6px;align-items:center">
              <span class="home-source">{{h.source}}</span>
              <span class="status-badge status-{{h.status}}">{{h.status|capitalize}}</span>
            </div>
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
  </div>
  {% endif %}

  <div class="cd">
    <div class="ch"><span class="ct">📍 Top Neighborhoods for Your Criteria</span></div>
    <div class="cb">
      <table>
        <tr><th>Neighborhood</th><th>Match Score</th><th>Avg Price</th><th>Parks</th><th>Water</th><th>Vibe</th></tr>
        {% for n in top5_neighborhoods %}
        <tr>
          <td><b>{{n.name}}</b></td>
          <td><span style="color:{{'var(--grn)' if n.score>=85 else 'var(--yel)'}};font-weight:700">{{n.score}}/100</span></td>
          <td>${{'%s' % '{:,}'.format(n.avg_price)}}</td>
          <td>{{'⭐' * n.park_score|int}}</td>
          <td>{{n.water}} mi</td>
          <td style="color:var(--dim);font-size:11px">{{n.vibe}}</td>
        </tr>
        {% endfor %}
      </table>
    </div>
  </div>
</div>

<!-- ═══ SEARCH ═══ -->
<div id="tab-search" {% if tab!='search' %}style="display:none"{% endif %}>
  <div class="cd">
    <div class="ch"><span class="ct">🔍 Live Search Engines — Pre-Filtered for Your Criteria</span></div>
    <div class="cb">
      <p style="font-size:18px;color:var(--dim);margin-bottom:16px">All links below are pre-configured: Jupiter FL · 2BR/1BA · 1,000–1,500 sqft · Max $800k. Click to open, find a home you like, copy the link and add it to Saved Homes.</p>
      <div class="source-grid">
        {% for name, src in sources.items() %}
        <a href="{{src.url}}" target="_blank" class="source-card" style="border-top:3px solid {{src.color}}">
          <div class="source-icon">{{src.icon}}</div>
          <div class="source-name" style="color:{{src.color}}">{{name}}</div>
          <div class="source-desc">Pre-filtered · 2BD/1BA · ≤$800k · 1,000–1,500 sqft · Jupiter FL</div>
          <div style="margin-top:10px;font-size:11px;color:var(--acc)">Open Search →</div>
        </a>
        {% endfor %}
      </div>
    </div>
  </div>

  <div class="cd">
    <div class="ch"><span class="ct">💡 Search Tips for Jupiter</span></div>
    <div class="cb">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:12px">
        <div style="background:var(--s2);border-radius:8px;padding:12px;border:1px solid var(--bdr)">
          <b style="color:var(--grn)">✅ Search in these zip codes</b><br><br>
          🏘 <b>33458</b> — Main Jupiter (Abacoa, central)<br>
          🏘 <b>33469</b> — Tequesta / NW Jupiter<br>
          🏘 <b>33477</b> — Jupiter Beach / Inlet area<br>
          🏘 <b>33478</b> — Jupiter Farms / West Jupiter
        </div>
        <div style="background:var(--s2);border-radius:8px;padding:12px;border:1px solid var(--bdr)">
          <b style="color:var(--yel)">⚡ Move Fast</b><br><br>
          Market is moving — avg 32 days on market but under-$800k homes go faster. Set up alerts on all platforms. Pre-approval in hand before you tour.
        </div>
        <div style="background:var(--s2);border-radius:8px;padding:12px;border:1px solid var(--bdr)">
          <b style="color:var(--acc)">🗓 Best Time to Buy</b><br><br>
          Jan–Mar = most inventory (snowbird season). Summer = less competition. Right now (Feb) is active — good timing.
        </div>
        <div style="background:var(--s2);border-radius:8px;padding:12px;border:1px solid var(--bdr)">
          <b style="color:var(--cyn)">💧 Water Access Check</b><br><br>
          Ask about: canal vs inlet vs Intracoastal, flood zone, insurance costs. Jupiter Inlet area = Zone AE (flood insurance req'd).
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ═══ SAVED ═══ -->
<div id="tab-saved" {% if tab!='saved' %}style="display:none"{% endif %}>
  {% if saved %}
  <div class="home-grid">
    {% for h in saved %}
    <div class="home-card" id="card-{{h.id}}">
      <div class="home-img">
        {% if h.image_url %}<img src="{{h.image_url}}" onerror="this.style.display='none'">{% else %}🏠{% endif %}
        <span class="home-star" onclick="toggleStar({{h.id}}, this)">{{' ⭐' if h.starred else ' 🤍'}}</span>
      </div>
      <div class="home-body">
        <div style="display:flex;justify-content:space-between;align-items:start">
          <div class="home-price">${{'%s' % '{:,}'.format(h.price)}}</div>
          <select style="width:auto;font-size:10px;padding:2px 6px" onchange="updateStatus({{h.id}},this.value)">
            <option value="new" {{'selected' if h.status=='new'}}>🆕 New</option>
            <option value="touring" {{'selected' if h.status=='touring'}}>👀 Touring</option>
            <option value="offer" {{'selected' if h.status=='offer'}}>📝 Offer</option>
            <option value="pass" {{'selected' if h.status=='pass'}}>❌ Pass</option>
          </select>
        </div>
        <div class="home-addr">📍 {{h.address}}</div>
        <div class="home-specs">
          <span class="home-spec">🛏 {{h.beds}}bd</span>
          <span class="home-spec">🛁 {{h.baths}}ba</span>
          <span class="home-spec">📐 {{'{:,}'.format(h.sqft)}} sqft</span>
          {% if h.sqft > 0 %}<span class="home-spec" style="color:var(--dim)">${{'%d' % (h.price/h.sqft)}}/sf</span>{% endif %}
        </div>
        <div style="margin-bottom:8px">
          <input type="text" placeholder="Notes..." value="{{h.notes}}" style="font-size:11px"
            onblur="updateNotes({{h.id}},this.value)">
        </div>
        <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">
          <span class="home-source">{{h.source}}</span>
          <span style="color:var(--dim);font-size:10px">Added {{h.added_date}}</span>
          {% if h.url %}<a href="{{h.url}}" target="_blank" style="color:var(--acc);font-size:11px;text-decoration:none">View Listing →</a>{% endif %}
          <button class="btn btn-red" style="font-size:10px;padding:2px 8px;margin-left:auto" onclick="deleteHome({{h.id}})">Remove</button>
        </div>
      </div>
    </div>
    {% endfor %}
  </div>
  {% else %}
  <div class="empty-state">
    <div class="big">🏠</div>
    <p>No saved homes yet.</p>
    <p style="margin-top:8px">Use the <b>Search</b> tab to find homes, then click <b>Add Home</b> to save them here.</p>
    <button class="btn btn-p" style="margin-top:16px" onclick="goTab('add')">➕ Add First Home</button>
  </div>
  {% endif %}
</div>

<!-- ═══ NEIGHBORHOODS ═══ -->
<div id="tab-neighborhoods" {% if tab!='neighborhoods' %}style="display:none"{% endif %}>
  <div class="cd">
    <div class="ch"><span class="ct">🏘 Jupiter Neighborhoods — Ranked for Your Criteria</span></div>
    <div class="cb">
      <p style="font-size:18px;color:var(--dim);margin-bottom:14px">Scored on: park access, water distance, neighborhood quality, value relative to price, vibe fit.</p>
      <div class="nbh-grid">
        {% for n in neighborhoods|sort(attribute='score',reverse=True) %}
        <div class="nbh-card">
          <div class="nbh-score {{'score-hi' if n.score>=85 else 'score-mid'}}">{{n.score}}</div>
          <div class="nbh-name">{{n.name}}</div>
          <div class="nbh-desc">{{n.desc}}</div>
          <div class="nbh-tags">
            <span class="ntag ntag-pk">🌳 Parks: {{n.park_score}}/10</span>
            <span class="ntag ntag-wt">💧 {{n.water}} mi to water</span>
            <span class="ntag ntag-pr">💰 Avg ${{'{:,}'.format(n.avg_price)}}</span>
          </div>
          <div style="font-size:10px;color:var(--dim);margin-top:8px">{{n.vibe}}</div>
        </div>
        {% endfor %}
      </div>
    </div>
  </div>
</div>

<!-- ═══ PARKS & WATER ═══ -->
<div id="tab-parks" {% if tab!='parks' %}style="display:none"{% endif %}>
  <div class="cd">
    <div class="ch"><span class="ct">🌳 Parks Near Jupiter</span></div>
    <div class="cb">
      <div class="park-list">
        {% for p in parks %}
        <div class="park-card">
          <div class="park-type">{{p.type}}</div>
          <div class="park-name">{{p.name}} {{p.rating}}</div>
          <div class="park-desc">{{p.desc}}</div>
          <div style="font-size:10px;color:var(--acc);margin-top:6px">📍 {{p.dist}}</div>
        </div>
        {% endfor %}
      </div>
    </div>
  </div>
  <div class="cd">
    <div class="ch"><span class="ct">🌊 Water Access — Why Jupiter is Special</span></div>
    <div class="cb">
      <div class="water-list">
        {% for w in water %}
        <div class="water-item">{{w}}</div>
        {% endfor %}
      </div>
    </div>
  </div>
</div>

<!-- ═══ MARKET ═══ -->
<div id="tab-market" {% if tab!='market' %}style="display:none"{% endif %}>
  <div class="cd">
    <div class="ch"><span class="ct">📈 Jupiter FL Market Intelligence</span></div>
    <div class="cb">
      <div class="market-grid">
        <div class="market-stat"><div class="market-label">Median Price</div><div class="market-val">$685k</div></div>
        <div class="market-stat"><div class="market-label">Price per sqft</div><div class="market-val">$485</div></div>
        <div class="market-stat"><div class="market-label">Avg Days on Mkt</div><div class="market-val">32</div></div>
        <div class="market-stat"><div class="market-label">Inventory</div><div class="market-val">Low</div></div>
        <div class="market-stat"><div class="market-label">YoY Trend</div><div class="market-val" style="color:var(--grn)">+4.2%</div></div>
        <div class="market-stat"><div class="market-label">Your Budget</div><div class="market-val" style="color:var(--acc)">$800k</div></div>
      </div>
      <div class="tip-box" style="margin-top:16px">
        💡 <b>Best timing:</b> {{market.best_months}}<br>
        ⚡ <b>Strategy:</b> {{market.tip}}
      </div>
      <div style="margin-top:14px;display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:12px">
        <div style="background:var(--s2);border-radius:8px;padding:12px;border:1px solid var(--bdr)">
          <b style="color:var(--grn)">✅ $800k gets you</b><br><br>
          • Updated 2/1 in Abacoa or Tequesta<br>
          • Small house in Jupiter Farms (more space)<br>
          • Townhome in Botanica (newer)<br>
          • Older CBS home near the Inlet
        </div>
        <div style="background:var(--s2);border-radius:8px;padding:12px;border:1px solid var(--bdr)">
          <b style="color:var(--red)">⚠️ Watch out for</b><br><br>
          • Flood insurance (ask FEMA zone first)<br>
          • HOA fees ($300–$800/mo in some areas)<br>
          • Older roofs (insurance nightmare in FL)<br>
          • Hurricane impact windows — check these
        </div>
        <div style="background:var(--s2);border-radius:8px;padding:12px;border:1px solid var(--bdr)">
          <b style="color:var(--yel)">🔑 Must-ask questions</b><br><br>
          • Age of roof? (Insurance loves <10yr)<br>
          • Impact windows/shutters included?<br>
          • HOA restrictions on rentals?<br>
          • Flood zone AE, X, or VE?
        </div>
        <div style="background:var(--s2);border-radius:8px;padding:12px;border:1px solid var(--bdr)">
          <b style="color:var(--acc)">📞 Good local agents</b><br><br>
          Search: "Jupiter FL buyer's agent"<br>
          Tip: Find someone who lives in Jupiter<br>
          and knows the neighborhoods, not just<br>
          a big-box agent parachuting in.
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ═══ ADD HOME ═══ -->
<div id="tab-add" {% if tab!='add' %}style="display:none"{% endif %}>
  <div class="cd">
    <div class="ch"><span class="ct">➕ Add a Home You Found</span></div>
    <div class="cb">
      <p style="font-size:18px;color:var(--dim);margin-bottom:16px">Find a home on Zillow, Redfin, or Realtor.com — then paste the details here to track it.</p>
      <div class="add-form" id="addForm">
        <div class="form-group form-full">
          <label>Address *</label>
          <input type="text" id="f-address" placeholder="123 Ocean Blvd, Jupiter FL 33458">
        </div>
        <div class="form-group">
          <label>Price ($) *</label>
          <input type="number" id="f-price" placeholder="750000">
        </div>
        <div class="form-group">
          <label>Square Feet</label>
          <input type="number" id="f-sqft" placeholder="1200">
        </div>
        <div class="form-group">
          <label>Bedrooms</label>
          <input type="number" id="f-beds" placeholder="2" value="2">
        </div>
        <div class="form-group">
          <label>Bathrooms</label>
          <input type="number" id="f-baths" placeholder="1" step="0.5" value="1">
        </div>
        <div class="form-group">
          <label>Source</label>
          <select id="f-source">
            <option>Zillow</option><option>Redfin</option><option>Realtor.com</option>
            <option>Trulia</option><option>Homes.com</option><option>Agent</option><option>Other</option>
          </select>
        </div>
        <div class="form-group">
          <label>Listing URL</label>
          <input type="url" id="f-url" placeholder="https://zillow.com/...">
        </div>
        <div class="form-group form-full">
          <label>Image URL (optional)</label>
          <input type="url" id="f-image" placeholder="https://...jpg">
        </div>
        <div class="form-group form-full">
          <label>Notes</label>
          <textarea id="f-notes" rows="3" placeholder="Nice backyard, needs new roof, loved the kitchen..."></textarea>
        </div>
        <div style="grid-column:1/-1">
          <button class="btn btn-p" onclick="addHome()" style="padding:10px 24px;font-size:13px">💾 Save Home</button>
          <span id="add-msg" style="margin-left:12px;font-size:12px;color:var(--grn)"></span>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ═══ MAGAZINES & ONLINE POSTS ═══ -->
<div id="tab-magazines" {% if tab!='magazines' %}style="display:none"{% endif %}>

  <div class="cd">
    <div class="ch">
      <span class="ct">📰 Live Real Estate News</span>
      <button class="btn btn-p" onclick="loadArticles()">🔄 Refresh</button>
    </div>
    <div class="cb" id="articles-container">
      <div style="text-align:center;padding:30px;color:var(--dim)">
        <div style="font-size:32px;margin-bottom:12px">📡</div>
        <div style="font-size:16px">Click Refresh to load latest real estate news</div>
        <button class="btn btn-p" style="margin-top:16px" onclick="loadArticles()">Load Articles</button>
      </div>
    </div>
  </div>

  <div class="cd">
    <div class="ch"><span class="ct">📚 Home & Design Magazines</span></div>
    <div class="cb">
      <div class="source-grid">
        {% for m in magazine_links %}
        <a href="{{m.url}}" target="_blank" class="source-card">
          <div class="source-icon">{{m.icon}}</div>
          <div class="source-name">{{m.name}}</div>
          <div class="source-desc">{{m.desc}}</div>
          <div style="margin-top:10px;font-size:13px;color:var(--acc)">Browse →</div>
        </a>
        {% endfor %}
      </div>
    </div>
  </div>

  <div class="cd">
    <div class="ch"><span class="ct">👥 Community & Social</span></div>
    <div class="cb">
      <p style="font-size:18px;color:var(--dim);margin-bottom:16px">Real people talking about Jupiter FL homes, neighborhoods, and buying experiences.</p>
      <div class="source-grid">
        {% for c in community_links %}
        <a href="{{c.url}}" target="_blank" class="source-card">
          <div class="source-icon">{{c.icon}}</div>
          <div class="source-name">{{c.name}}</div>
          <div class="source-desc">{{c.desc}}</div>
          <div style="margin-top:10px;font-size:13px;color:var(--acc)">Open →</div>
        </a>
        {% endfor %}
      </div>
    </div>
  </div>

  <div class="cd">
    <div class="ch"><span class="ct">🔎 Quick Google Searches — Jupiter FL</span></div>
    <div class="cb">
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px">
        {% set searches = [
          ('Jupiter FL homes for sale 2025','https://www.google.com/search?q=Jupiter+FL+homes+for+sale+2025'),
          ('Jupiter FL real estate market 2025','https://www.google.com/search?q=Jupiter+FL+real+estate+market+2025'),
          ('Best neighborhoods Jupiter FL','https://www.google.com/search?q=best+neighborhoods+Jupiter+Florida'),
          ('Jupiter FL flood zones map','https://www.google.com/search?q=Jupiter+FL+flood+zone+map'),
          ('Moving to Jupiter Florida','https://www.google.com/search?q=moving+to+Jupiter+Florida+pros+cons'),
          ('Jupiter FL HOA communities','https://www.google.com/search?q=Jupiter+FL+HOA+communities+homes'),
          ('Abacoa Jupiter FL homes','https://www.google.com/search?q=Abacoa+Jupiter+FL+homes+for+sale'),
          ('Tequesta FL homes for sale','https://www.google.com/search?q=Tequesta+FL+homes+for+sale'),
          ('Jupiter FL hurricane impact windows','https://www.google.com/search?q=Jupiter+FL+hurricane+impact+windows+cost'),
          ('Jupiter FL property taxes','https://www.google.com/search?q=Jupiter+FL+property+tax+rate+2025'),
          ('Jupiter FL home inspection tips','https://www.google.com/search?q=Jupiter+FL+home+inspection+what+to+look+for'),
          ('Jupiter FL waterfront homes under 800k','https://www.google.com/search?q=Jupiter+FL+waterfront+homes+under+800000'),
        ] %}
        {% for label, url in searches %}
        <a href="{{url}}" target="_blank" style="background:var(--s2);border:1px solid var(--bdr);border-radius:8px;padding:12px;text-decoration:none;display:block;transition:all .2s" onmouseover="this.style.borderColor='var(--acc)'" onmouseout="this.style.borderColor='var(--bdr)'">
          <span style="font-size:16px;color:var(--acc)">🔍</span>
          <span style="font-size:15px;color:var(--txt);margin-left:8px">{{label}}</span>
        </a>
        {% endfor %}
      </div>
    </div>
  </div>

</div>

</div><!-- /main -->

<script>
function goTab(t){
  document.querySelectorAll('[id^="tab-"]').forEach(el=>el.style.display='none');
  document.getElementById('tab-'+t).style.display='';
  document.querySelectorAll('.nb').forEach(b=>b.classList.remove('a'));
  event.target.classList.add('a');
  history.replaceState(null,'','?tab='+t);
}

function toggleStar(id, el){
  fetch('/star/'+id,{method:'POST'})
    .then(r=>r.json())
    .then(d=>{ el.textContent = d.starred ? ' ⭐' : ' 🤍'; });
}

function updateStatus(id, val){
  fetch('/update_home/'+id,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:val})});
}

function updateNotes(id, val){
  fetch('/update_home/'+id,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({notes:val})});
}

function deleteHome(id){
  if(!confirm('Remove this home?')) return;
  fetch('/delete_home/'+id,{method:'POST'})
    .then(()=>{ document.getElementById('card-'+id)?.remove(); });
}

function loadArticles(){
  const container = document.getElementById('articles-container');
  container.innerHTML = '<div style="text-align:center;padding:30px;color:var(--dim);font-size:16px">⏳ Fetching latest articles...</div>';
  fetch('/api/articles')
    .then(r=>r.json())
    .then(arts=>{
      if(!arts.length){
        container.innerHTML='<div style="text-align:center;padding:30px;color:var(--dim);font-size:16px">No articles found. Try again shortly.</div>';
        return;
      }
      let html='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:14px">';
      arts.forEach(a=>{
        html+=`<a href="${a.url}" target="_blank" style="background:var(--s2);border:1px solid var(--bdr);border-radius:10px;padding:16px;text-decoration:none;display:block;transition:all .2s;border-top:3px solid ${a.color}" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='none'">
          <div style="display:flex;gap:8px;align-items:center;margin-bottom:10px">
            <span style="font-size:20px">${a.icon}</span>
            <span style="font-size:15px;color:var(--dim);font-weight:600;text-transform:uppercase">${a.source}</span>
            <span style="font-size:11px;color:var(--dim);margin-left:auto">${a.pub}</span>
          </div>
          <div style="font-size:20px;font-weight:600;color:var(--txt);margin-bottom:8px;line-height:1.4">${a.title}</div>
          <div style="font-size:17px;color:var(--dim);line-height:1.5">${a.desc}</div>
          <div style="font-size:17px;color:var(--acc);margin-top:10px">Read article →</div>
        </a>`;
      });
      html+='</div>';
      container.innerHTML=html;
    })
    .catch(e=>{ container.innerHTML='<div style="text-align:center;padding:20px;color:var(--red);font-size:15px">Error loading articles. Check connection.</div>'; });
}

function addHome(){
  const d = {
    address: document.getElementById('f-address').value,
    price: document.getElementById('f-price').value,
    sqft: document.getElementById('f-sqft').value,
    beds: document.getElementById('f-beds').value,
    baths: document.getElementById('f-baths').value,
    source: document.getElementById('f-source').value,
    url: document.getElementById('f-url').value,
    image_url: document.getElementById('f-image').value,
    notes: document.getElementById('f-notes').value,
  };
  if(!d.address || !d.price){ alert('Address and price are required'); return; }
  fetch('/add_home',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)})
    .then(r=>r.json())
    .then(r=>{
      if(r.ok){
        document.getElementById('add-msg').textContent='✅ Saved!';
        setTimeout(()=>{ window.location.href='?tab=saved'; },800);
      }
    });
}
</script>
</body></html>
"""

ONLINE_SOURCES = [
    {
        'name': 'Realtor.com News',
        'url': 'https://www.realtor.com/news/feed/',
        'color': '#cc0000',
        'icon': '🏡',
        'tags': ['market','buying','trends']
    },
    {
        'name': 'Curbed',
        'url': 'https://www.curbed.com/rss/index.xml',
        'color': '#e84545',
        'icon': '🏠',
        'tags': ['design','listings','market']
    },
]

MAGAZINE_LINKS = [
    {'name':'Architectural Digest','url':'https://www.architecturaldigest.com/search?q=florida+home','icon':'✨','desc':'Florida home design & architecture'},
    {'name':'Dwell','url':'https://www.dwell.com/search?q=florida','icon':'🏗','desc':'Modern homes & architecture'},
    {'name':'This Old House','url':'https://www.thisoldhouse.com/search?q=florida','icon':'🔨','desc':'Renovation, buying tips, projects'},
    {'name':'Better Homes & Gardens','url':'https://www.bhg.com/decorating/home-tour/','icon':'🌸','desc':'Home tours & decorating ideas'},
    {'name':'House Beautiful','url':'https://www.housebeautiful.com/design-inspiration/','icon':'🪟','desc':'Interior design inspiration'},
    {'name':'Home Beautiful FL','url':'https://www.google.com/search?q=jupiter+florida+homes+for+sale+magazine&tbm=nws','icon':'🌴','desc':'Jupiter FL homes in the news'},
]

COMMUNITY_LINKS = [
    {'name':'Reddit r/FirstTimeHomeBuyer','url':'https://www.reddit.com/r/FirstTimeHomeBuyer/search/?q=jupiter+florida&sort=new','icon':'👥','desc':'Real buyer experiences in Jupiter FL'},
    {'name':'Reddit r/florida','url':'https://www.reddit.com/r/florida/search/?q=jupiter+homes&sort=new','icon':'🌴','desc':'FL community discussions'},
    {'name':'Reddit r/realestate','url':'https://www.reddit.com/r/realestate/search/?q=jupiter+florida&sort=new','icon':'🏠','desc':'Real estate advice & market talk'},
    {'name':'Nextdoor Jupiter FL','url':'https://nextdoor.com/city/jupiter--fl/','icon':'🏘','desc':'Local Jupiter neighborhood discussions'},
    {'name':'Google News — Jupiter Homes','url':'https://news.google.com/search?q=jupiter+florida+real+estate+homes&hl=en-US','icon':'📰','desc':'Latest Jupiter FL real estate news'},
    {'name':'Facebook Jupiter FL Homes','url':'https://www.facebook.com/marketplace/jupiter-fl/propertyrentals/?minPrice=0&maxPrice=800000&propertyType=house&minBedrooms=2','icon':'📘','desc':'Facebook Marketplace listings'},
]

def fetch_articles(limit=12):
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
    articles = []
    for src in ONLINE_SOURCES:
        try:
            r = requests.get(src['url'], headers=headers, timeout=7)
            if r.status_code != 200:
                continue
            root = ET.fromstring(r.text)
            items = root.findall('.//item')[:8]
            for item in items:
                title = item.findtext('title','').strip()
                link = item.findtext('link','').strip()
                desc = item.findtext('description','').strip()
                pub = item.findtext('pubDate','').strip()
                # Clean HTML from description
                import re
                desc = re.sub(r'<[^>]+>', '', htmllib.unescape(desc))[:200]
                if title and link:
                    articles.append({
                        'title': htmllib.unescape(title),
                        'url': link,
                        'desc': desc,
                        'source': src['name'],
                        'icon': src['icon'],
                        'color': src['color'],
                        'pub': pub[:16] if pub else '',
                        'tags': src['tags']
                    })
        except Exception as e:
            pass
    return articles[:limit]

@app.route('/api/articles')
def get_articles():
    arts = fetch_articles(20)
    return jsonify(arts)


@app.route('/favorites')
def favorites():
    conn = get_db()
    starred = conn.execute("SELECT * FROM saved_homes WHERE starred=1 ORDER BY added_date DESC").fetchall()
    conn.close()
    return render_template_string(FAV_TEMPLATE, homes=starred)


FAV_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>🌴 Our Jupiter Favorites</title>
<style>
:root{--bg:#0f1117;--s1:#181b27;--s2:#1e2235;--bdr:#2a2e42;--txt:#e2e4eb;--dim:#6b7280;--acc:#4f8ff7;--grn:#34d399;--yel:#fbbf24;--red:#f87171}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--txt);min-height:100vh;font-size:18px}
.hdr{background:linear-gradient(135deg,#0f2040,#1a3060);padding:18px 20px;text-align:center}
.hdr h1{font-size:26px;font-weight:700}.hdr p{font-size:16px;color:#94a3b8;margin-top:4px}
.main{padding:16px;max-width:700px;margin:0 auto}
.card{background:var(--s1);border:1px solid var(--bdr);border-radius:14px;margin-bottom:18px;overflow:hidden}
.card-img{width:100%;height:200px;background:linear-gradient(135deg,var(--s2),var(--s1));display:flex;align-items:center;justify-content:center;font-size:64px}
.card-img img{width:100%;height:100%;object-fit:cover}
.card-body{padding:18px}
.price{font-size:32px;font-weight:700;color:var(--grn)}
.addr{font-size:17px;color:var(--dim);margin:6px 0 12px}
.specs{display:flex;gap:16px;font-size:17px;font-weight:600;margin-bottom:12px}
.notes{background:var(--s2);border-radius:8px;padding:12px;font-size:16px;color:var(--dim);margin-bottom:14px}
.actions{display:flex;gap:10px;flex-wrap:wrap}
.btn{padding:12px 20px;border-radius:10px;font-size:16px;font-weight:600;text-decoration:none;display:inline-block;text-align:center}
.btn-primary{background:var(--acc);color:#fff}
.btn-outline{border:2px solid var(--bdr);color:var(--txt);background:var(--s2)}
.badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:14px;font-weight:600}
.badge-new{background:rgba(79,143,247,.2);color:var(--acc)}
.badge-touring{background:rgba(251,191,36,.2);color:var(--yel)}
.badge-offer{background:rgba(167,139,250,.2);color:#a78bfa}
.empty{text-align:center;padding:60px 20px}
.empty .icon{font-size:64px;margin-bottom:16px}
.empty p{font-size:19px;color:var(--dim)}
.back{display:block;text-align:center;padding:14px;color:var(--acc);font-size:17px;text-decoration:none;margin-bottom:16px}
</style>
</head>
<body>
<div class="hdr">
  <h1>⭐ Our Jupiter Favorites</h1>
  <p>Homes Chris starred — tap to view listing</p>
</div>
<div class="main">
  <a href="/" class="back">← Back to Full Dashboard</a>
  {% if homes %}
    {% for h in homes %}
    <div class="card">
      <div class="card-img">
        {% if h.image_url %}<img src="{{h.image_url}}" onerror="this.parentElement.textContent='🏠'">{% else %}🏠{% endif %}
      </div>
      <div class="card-body">
        <div class="price">${{'%s' % '{:,}'.format(h.price)}}</div>
        <div class="addr">📍 {{h.address}}</div>
        <div class="specs">
          <span>🛏 {{h.beds}} bed</span>
          <span>🛁 {{h.baths}} bath</span>
          <span>📐 {{'{:,}'.format(h.sqft)}} sqft</span>
        </div>
        {% if h.notes %}<div class="notes">💬 {{h.notes}}</div>{% endif %}
        <div style="display:flex;gap:8px;align-items:center;margin-bottom:14px">
          <span class="badge badge-{{h.status}}">{{h.status|capitalize}}</span>
          <span style="font-size:14px;color:var(--dim)">via {{h.source}} · {{h.added_date}}</span>
        </div>
        <div class="actions">
          {% if h.url %}
          <a href="{{h.url}}" target="_blank" class="btn btn-primary">🔗 View Listing</a>
          {% endif %}
        </div>
      </div>
    </div>
    {% endfor %}
  {% else %}
  <div class="empty">
    <div class="icon">⭐</div>
    <p>No favorites yet.</p>
    <p style="margin-top:8px;font-size:16px">Chris hasn't starred any homes yet.<br>Check back soon!</p>
  </div>
  {% endif %}
</div>
</body></html>"""

if __name__ == '__main__':
    print("🌴 Jupiter Home Finder running at http://localhost:8765")
    app.run(host='0.0.0.0', port=8765, debug=False)
