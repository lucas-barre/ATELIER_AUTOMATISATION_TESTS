import sqlite3
import json
import os

# SQLite DB path (placed in same directory as storage.py to be portable on PythonAnywhere)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            api TEXT NOT NULL,
            passed INTEGER NOT NULL,
            failed INTEGER NOT NULL,
            error_rate REAL NOT NULL,
            availability REAL NOT NULL,
            latency_ms_avg REAL NOT NULL,
            latency_ms_p95 REAL NOT NULL,
            tests_json TEXT NOT NULL
        )
    """)
    # Ensure the availability column exists for older DBs
    cursor.execute("PRAGMA table_info(runs)")
    cols = [row["name"] for row in cursor.fetchall()]
    if "availability" not in cols:
        cursor.execute("ALTER TABLE runs ADD COLUMN availability REAL NOT NULL DEFAULT 0")
    conn.commit()
    conn.close()

def save_run(run_data):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO runs (timestamp, api, passed, failed, error_rate, availability, latency_ms_avg, latency_ms_p95, tests_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_data["timestamp"],
        run_data["api"],
        run_data["summary"]["passed"],
        run_data["summary"]["failed"],
        run_data["summary"]["error_rate"],
        run_data["summary"].get("availability", 0),
        run_data["summary"]["latency_ms_avg"],
        run_data["summary"]["latency_ms_p95"],
        json.dumps(run_data["tests"])
    ))
    conn.commit()
    conn.close()

def list_runs(limit=50):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM runs ORDER BY timestamp DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    
    runs = []
    for r in rows:
        runs.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "api": r["api"],
            "summary": {
                "total": r["passed"] + r["failed"],
                "passed": r["passed"],
                "failed": r["failed"],
                "error_rate": r["error_rate"],
                "availability": r["availability"],
                "latency_ms_avg": r["latency_ms_avg"],
                "latency_ms_p95": r["latency_ms_p95"]
            },
            "tests": json.loads(r["tests_json"])
        })
    conn.close()
    return runs
