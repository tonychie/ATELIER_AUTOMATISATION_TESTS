"""Persistance SQLite de l'historique des runs de tests."""
import json
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'web',
                timestamp TEXT NOT NULL,
                passed INTEGER NOT NULL,
                failed INTEGER NOT NULL,
                error_rate REAL NOT NULL,
                availability_pct REAL NOT NULL DEFAULT 100.0,
                latency_ms_avg REAL NOT NULL,
                latency_ms_p95 REAL NOT NULL,
                tests_json TEXT NOT NULL
            )
            """
        )
        existing_cols = {row["name"] for row in conn.execute("PRAGMA table_info(runs)")}
        if "source" not in existing_cols:
            conn.execute("ALTER TABLE runs ADD COLUMN source TEXT NOT NULL DEFAULT 'web'")
        if "availability_pct" not in existing_cols:
            conn.execute("ALTER TABLE runs ADD COLUMN availability_pct REAL NOT NULL DEFAULT 100.0")


def save_run(run: dict) -> int:
    init_db()
    summary = run["summary"]
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO runs (api, source, timestamp, passed, failed, error_rate, availability_pct, latency_ms_avg, latency_ms_p95, tests_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run["api"],
                run.get("source", "web"),
                run["timestamp"],
                summary["passed"],
                summary["failed"],
                summary["error_rate"],
                summary.get("availability_pct", 100.0),
                summary["latency_ms_avg"],
                summary["latency_ms_p95"],
                json.dumps(run["tests"], ensure_ascii=False),
            ),
        )
        return cur.lastrowid


def _row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "api": row["api"],
        "source": row["source"],
        "timestamp": row["timestamp"],
        "summary": {
            "passed": row["passed"],
            "failed": row["failed"],
            "error_rate": row["error_rate"],
            "availability_pct": row["availability_pct"],
            "latency_ms_avg": row["latency_ms_avg"],
            "latency_ms_p95": row["latency_ms_p95"],
        },
        "tests": json.loads(row["tests_json"]),
    }


def list_runs(limit: int = 20) -> list:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_last_run() -> dict | None:
    runs = list_runs(limit=1)
    return runs[0] if runs else None
