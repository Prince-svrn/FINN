"""Small WAL-mode SQLite store: immutable content, versioned cache and telemetry."""
import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv('FINN_DB', ROOT/'runtime/finn.db'))

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=20)
    db.row_factory = sqlite3.Row
    db.executescript('''
      PRAGMA journal_mode=WAL;
      CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT NOT NULL, created REAL NOT NULL);
      CREATE TABLE IF NOT EXISTS documents (hash TEXT PRIMARY KEY, source_url TEXT, pages TEXT, created REAL);
      CREATE TABLE IF NOT EXISTS telemetry (id INTEGER PRIMARY KEY, at REAL, task TEXT, tier INTEGER, model TEXT,
         input_tokens INTEGER, output_tokens INTEGER, cost REAL, latency_ms REAL, cache_hit INTEGER, status TEXT);
      CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS filings (id TEXT PRIMARY KEY, symbol TEXT, published_at TEXT, value TEXT);
      CREATE TABLE IF NOT EXISTS pins (id TEXT PRIMARY KEY, value TEXT, created REAL);
    ''')
    return db

def get(key, ttl=None):
    with connect() as db:
        r = db.execute('SELECT * FROM cache WHERE key=?', (key,)).fetchone()
    if not r or ttl is not None and time.time()-r['created'] > ttl: return None
    return json.loads(r['value'])

def put(key, value):
    with connect() as db: db.execute('INSERT OR REPLACE INTO cache VALUES (?,?,?)', (key,json.dumps(value, allow_nan=False),time.time()))

def digest(raw): return hashlib.sha256(raw).hexdigest()

def log(task, tier=0, model='deterministic', input_tokens=0, output_tokens=0, cost=0., latency_ms=0., cache_hit=False, status='ok'):
    with connect() as db:
        db.execute('INSERT INTO telemetry(at,task,tier,model,input_tokens,output_tokens,cost,latency_ms,cache_hit,status) VALUES (?,?,?,?,?,?,?,?,?,?)',
                   (time.time(),task,tier,model,input_tokens,output_tokens,cost,latency_ms,int(cache_hit),status))

def telemetry():
    with connect() as db:
        rows = [dict(r) for r in db.execute('SELECT * FROM telemetry ORDER BY id DESC LIMIT 100')]
        sums = dict(db.execute('SELECT COUNT(*) calls, COALESCE(SUM(cost),0) cost, COALESCE(SUM(cache_hit),0) cache_hits, COALESCE(SUM(input_tokens),0) input_tokens, COALESCE(SUM(output_tokens),0) output_tokens, COALESCE(SUM(CASE WHEN tier>0 AND cost IS NULL THEN 1 ELSE 0 END),0) unpriced_calls FROM telemetry').fetchone())
    return {**sums, 'requests': rows}
