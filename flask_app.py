from datetime import datetime, timezone

from flask import Flask, render_template, jsonify

from storage import init_db, save_run, list_runs, get_last_run
from tester.runner import run_all

app = Flask(__name__)

MIN_SECONDS_BETWEEN_RUNS = 60  # anti-spam : pas plus d'un run manuel par minute

init_db()


@app.get("/")
def consignes():
    return render_template('consignes.html')


@app.get("/run")
def run():
    last = get_last_run()
    if last:
        last_ts = datetime.fromisoformat(last["timestamp"])
        elapsed = (datetime.now(timezone.utc) - last_ts).total_seconds()
        if elapsed < MIN_SECONDS_BETWEEN_RUNS:
            wait = int(MIN_SECONDS_BETWEEN_RUNS - elapsed)
            return jsonify({"error": f"Trop de requêtes, réessayez dans {wait}s"}), 429

    run_result = run_all()
    save_run(run_result)
    return jsonify(run_result)


@app.get("/dashboard")
def dashboard():
    runs = list_runs(limit=20)
    last = runs[0] if runs else None
    max_latency = max((r["summary"]["latency_ms_avg"] for r in runs), default=0)
    return render_template("dashboard.html", runs=runs, last=last, max_latency=max_latency)


@app.get("/api/runs")
def api_runs():
    return jsonify(list_runs(limit=100))


@app.get("/health")
def health():
    try:
        last = get_last_run()
        return jsonify({
            "status": "ok",
            "db": "ok",
            "last_run_at": last["timestamp"] if last else None,
        })
    except Exception as exc:
        return jsonify({"status": "error", "details": str(exc)}), 500


if __name__ == "__main__":
    # utile en local uniquement
    app.run(host="0.0.0.0", port=5000, debug=True)
