from flask import Flask, render_template, jsonify, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

# Import custom modules
from tester.runner import run_all_tests
from storage import save_run, list_runs, init_db, DB_PATH

app = Flask(__name__)

# Initialize the database on startup
init_db()

@app.route("/")
def index():
    # Redirect to dashboard for premium entrypoint,
    # but still let consignes be accessible at /consignes.
    return redirect(url_for("dashboard"))

@app.route("/consignes")
def consignes():
    return render_template("consignes.html")

@app.route("/dashboard")
def dashboard():
    runs = list_runs(limit=50)
    latest_run = runs[0] if runs else None
    return render_template("dashboard.html", latest_run=latest_run, runs=runs)

@app.route("/run", methods=["GET", "POST"])
def run_tests():
    if request.method == "POST":
        # Dynamic execution trigger
        run_result = run_all_tests()
        save_run(run_result)
        return jsonify(run_result)
    else:
        # GET request returns the last run JSON or runs one if empty
        runs = list_runs(limit=1)
        if runs:
            return jsonify(runs[0])
        else:
            run_result = run_all_tests()
            save_run(run_result)
            return jsonify(run_result)

@app.route("/health")
def health():
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "database": "connected",
        "api_connectivity": "unknown"
    }
    
    # Check SQLite connection
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
    except Exception as e:
        status["status"] = "unhealthy"
        status["database"] = f"error: {str(e)}"
        
    # Quick API connectivity check with Frankfurter
    try:
        from tester.client import APIClient
        client = APIClient()
        res = client.request("GET", "/currencies")
        if res["status_code"] == 200:
            status["api_connectivity"] = "ok"
        else:
            status["api_connectivity"] = f"http_status_{res['status_code']}"
    except Exception as e:
        status["api_connectivity"] = f"error: {str(e)}"
        
    # Overall health check
    if status["database"] != "connected" or status["api_connectivity"] != "ok":
        status["status"] = "degraded"
        
    return jsonify(status)

if __name__ == "__main__":
    # local debug
    app.run(host="0.0.0.0", port=5000, debug=True)
