"""Tests 'as code' pour l'API Agify (https://api.agify.io).

Chaque test renvoie un dict: {"name", "status": "PASS"|"FAIL", "latency_ms", "details"}.
Une exception dans un test ne doit jamais interrompre les autres (robustesse du runner).
"""
from .client import timed_get

BASE_URL = "https://api.agify.io"


def _result(name, ok, latency_ms, details=""):
    return {
        "name": name,
        "status": "PASS" if ok else "FAIL",
        "latency_ms": latency_ms,
        "details": details,
    }


def test_status_200_basic():
    status, body, latency_ms, error, _ = timed_get(f"{BASE_URL}?name=michael")
    ok = status == 200 and error is None
    return _result("GET /?name=michael -> 200", ok, latency_ms, error or f"status={status}")


def test_content_type_json():
    status, body, latency_ms, error, content_type = timed_get(f"{BASE_URL}?name=emma")
    ok = status == 200 and "application/json" in (content_type or "")
    return _result("Content-Type JSON", ok, latency_ms, error or f"content_type={content_type}")


def test_required_fields_present():
    status, body, latency_ms, error, _ = timed_get(f"{BASE_URL}?name=sophia")
    ok = status == 200 and isinstance(body, dict) and {"name", "age", "count"} <= set(body.keys())
    return _result("Champs obligatoires (name, age, count)", ok, latency_ms, error or f"keys={list(body.keys()) if isinstance(body, dict) else body}")


def test_field_types():
    status, body, latency_ms, error, _ = timed_get(f"{BASE_URL}?name=lucas")
    ok = (
        status == 200
        and isinstance(body, dict)
        and isinstance(body.get("name"), str)
        and (body.get("age") is None or isinstance(body.get("age"), int))
        and isinstance(body.get("count"), int)
    )
    return _result("Types des champs (name:str, age:int|null, count:int)", ok, latency_ms, error or f"body={body}")


def test_name_echoed():
    status, body, latency_ms, error, _ = timed_get(f"{BASE_URL}?name=julien")
    ok = status == 200 and isinstance(body, dict) and body.get("name") == "julien"
    return _result("Le champ 'name' reflète le paramètre envoyé", ok, latency_ms, error or f"body={body}")


def test_unknown_name_still_200():
    status, body, latency_ms, error, _ = timed_get(f"{BASE_URL}?name=xzqvtnobpq")
    ok = status == 200 and isinstance(body, dict) and body.get("count") == 0
    return _result("Prénom inconnu -> 200 avec count=0 (pas d'erreur serveur)", ok, latency_ms, error or f"body={body}")


def test_missing_param_error_code():
    status, body, latency_ms, error, _ = timed_get(f"{BASE_URL}?")
    ok = status in (400, 422)
    return _result("Paramètre 'name' manquant -> code d'erreur attendu (400/422)", ok, latency_ms, error or f"status={status}")


def test_latency_under_threshold():
    status, body, latency_ms, error, _ = timed_get(f"{BASE_URL}?name=noa")
    ok = status == 200 and latency_ms < 3000
    return _result("Latence d'un appel < 3000ms", ok, latency_ms, error or f"latency={latency_ms}ms")


ALL_TESTS = [
    test_status_200_basic,
    test_content_type_json,
    test_required_fields_present,
    test_field_types,
    test_name_echoed,
    test_unknown_name_still_200,
    test_missing_param_error_code,
    test_latency_under_threshold,
]
