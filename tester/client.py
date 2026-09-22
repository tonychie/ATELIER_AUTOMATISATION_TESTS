"""Client HTTP minimaliste : timeout strict, 1 retry max sur 429/5xx/timeout, mesure de latence."""
import json
import time
import urllib.error
import urllib.request

TIMEOUT_S = 4
RETRY_BACKOFF_S = 1


def timed_get(url, timeout=TIMEOUT_S, max_retries=1):
    """Effectue un GET et renvoie (status_code, json_body, latency_ms, error).

    - Timeout strict (par défaut 4s).
    - 1 retry max si timeout, 429 (rate limit) ou 5xx.
    - Ne lève jamais d'exception : les erreurs réseau sont renvoyées dans `error`.
    """
    attempt = 0
    last_error = None

    while attempt <= max_retries:
        start = time.perf_counter()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "atelier-tests/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                latency_ms = round((time.perf_counter() - start) * 1000, 1)
                status = resp.status
                content_type = resp.headers.get("Content-Type", "")
                raw = resp.read()
                body = None
                if "json" in content_type:
                    try:
                        body = json.loads(raw.decode("utf-8"))
                    except json.JSONDecodeError:
                        body = None
                if status in (429, 500, 502, 503, 504) and attempt < max_retries:
                    attempt += 1
                    time.sleep(RETRY_BACKOFF_S)
                    continue
                return status, body, latency_ms, None, content_type

        except urllib.error.HTTPError as e:
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            if e.code in (429, 500, 502, 503, 504) and attempt < max_retries:
                attempt += 1
                time.sleep(RETRY_BACKOFF_S)
                continue
            try:
                raw = e.read()
                body = json.loads(raw.decode("utf-8"))
            except Exception:
                body = None
            return e.code, body, latency_ms, f"HTTP {e.code}", e.headers.get("Content-Type", "") if e.headers else ""

        except (urllib.error.URLError, TimeoutError) as e:
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            last_error = str(e)
            if attempt < max_retries:
                attempt += 1
                time.sleep(RETRY_BACKOFF_S)
                continue
            return None, None, latency_ms, f"Erreur réseau/timeout: {last_error}", ""

    return None, None, 0.0, "Nombre de tentatives épuisé", ""
