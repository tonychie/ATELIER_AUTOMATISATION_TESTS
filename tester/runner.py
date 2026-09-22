"""Exécute la suite de tests et calcule les métriques QoS (latence avg/p95, taux d'erreur)."""
import datetime
import statistics

from .tests import ALL_TESTS

API_NAME = "Agify"


def _percentile_95(values):
    if not values:
        return 0.0
    s = sorted(values)
    idx = min(len(s) - 1, int(round(0.95 * (len(s) - 1))))
    return s[idx]


def run_all():
    results = []
    for test_fn in ALL_TESTS:
        try:
            results.append(test_fn())
        except Exception as exc:  # une erreur de test ne doit jamais casser le run
            results.append({
                "name": getattr(test_fn, "__name__", "unknown"),
                "status": "FAIL",
                "latency_ms": 0.0,
                "details": f"Exception: {exc}",
            })

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = len(results) - passed
    latencies = [r["latency_ms"] for r in results if r["latency_ms"]]
    error_rate = round(failed / len(results), 4) if results else 0.0

    summary = {
        "passed": passed,
        "failed": failed,
        "error_rate": error_rate,
        "latency_ms_avg": round(statistics.mean(latencies), 1) if latencies else 0.0,
        "latency_ms_p95": round(_percentile_95(latencies), 1),
    }

    run = {
        "api": API_NAME,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "summary": summary,
        "tests": results,
    }
    return run
