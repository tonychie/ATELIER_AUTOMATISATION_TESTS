"""Tests 'as code' pour l'API Agify (https://api.agify.io).

Chaque test renvoie un dict: {"name", "category", "status": "PASS"|"FAIL", "latency_ms", "details"}.
Categories : contract (contrat fonctionnel), robustness (entrees invalides / rafale), qos (latence).
Une exception dans un test ne doit jamais interrompre les autres (robustesse du runner).
"""
from .client import timed_get

BASE_URL = "https://api.agify.io"


def _result(name, category, ok, latency_ms, details=""):
    return {
        "name": name,
        "category": category,
        "status": "PASS" if ok else "FAIL",
        "latency_ms": latency_ms,
        "details": details,
    }


def test_status_200_basic():
    status, body, latency_ms, error, _ = timed_get(f"{BASE_URL}?name=michael")
    ok = status == 200 and error is None
    return _result("status_200_basic", "contract", ok, latency_ms, error or f"status={status}")


def test_content_type_json():
    status, body, latency_ms, error, content_type = timed_get(f"{BASE_URL}?name=emma")
    ok = status == 200 and "application/json" in (content_type or "")
    return _result("content_type_json", "contract", ok, latency_ms, error or f"content_type={content_type}")


def test_required_fields_present():
    status, body, latency_ms, error, _ = timed_get(f"{BASE_URL}?name=sophia")
    ok = status == 200 and isinstance(body, dict) and {"name", "age", "count"} <= set(body.keys())
    return _result("required_fields_present", "contract", ok, latency_ms, error or f"keys={list(body.keys()) if isinstance(body, dict) else body}")


def test_field_types():
    status, body, latency_ms, error, _ = timed_get(f"{BASE_URL}?name=lucas")
    ok = (
        status == 200
        and isinstance(body, dict)
        and isinstance(body.get("name"), str)
        and (body.get("age") is None or isinstance(body.get("age"), int))
        and isinstance(body.get("count"), int)
    )
    return _result("field_types", "contract", ok, latency_ms, error or f"body={body}")


def test_name_echoed():
    status, body, latency_ms, error, _ = timed_get(f"{BASE_URL}?name=julien")
    ok = status == 200 and isinstance(body, dict) and body.get("name") == "julien"
    return _result("name_echoed", "contract", ok, latency_ms, error or f"body={body}")


def test_batch_multiple_names():
    status, body, latency_ms, error, _ = timed_get(f"{BASE_URL}?name[]=michael&name[]=julien")
    ok = status == 200 and isinstance(body, list) and len(body) == 2
    return _result("batch_multiple_names", "contract", ok, latency_ms, error or f"body={body}")


def test_unknown_name_still_200():
    status, body, latency_ms, error, _ = timed_get(f"{BASE_URL}?name=xzqvtnobpq")
    ok = status == 200 and isinstance(body, dict) and body.get("count") == 0
    return _result("unknown_name_handled", "robustness", ok, latency_ms, error or f"body={body}")


def test_missing_param_error_code():
    status, body, latency_ms, error, _ = timed_get(f"{BASE_URL}?")
    ok = status in (400, 422)
    return _result("missing_param_returns_4xx", "robustness", ok, latency_ms, error or f"status={status}")


def test_burst_is_handled():
    latencies = []
    for name in ("alex", "sam", "noa"):
        status, body, latency_ms, error, _ = timed_get(f"{BASE_URL}?name={name}")
        latencies.append(latency_ms)
        if status is None or status >= 500:
            return _result("burst_is_handled", "robustness", False, sum(latencies), f"status={status} error={error}")
    return _result("burst_is_handled", "robustness", True, sum(latencies), "3 appels rapprochés, aucun 5xx")


def test_latency_under_threshold():
    status, body, latency_ms, error, _ = timed_get(f"{BASE_URL}?name=noa")
    ok = status == 200 and latency_ms < 3000
    return _result("latency_under_sla", "qos", ok, latency_ms, error or f"latency={latency_ms}ms (SLA 3000ms)")


ALL_TESTS = [
    test_status_200_basic,
    test_content_type_json,
    test_required_fields_present,
    test_field_types,
    test_name_echoed,
    test_batch_multiple_names,
    test_unknown_name_still_200,
    test_missing_param_error_code,
    test_burst_is_handled,
    test_latency_under_threshold,
]
