import logging
import urllib.request
import urllib.error
import time

# Endpoints to monitor — edit freely
ENDPOINTS = [
    {"name": "Google", "url": "https://www.google.com"},
    {"name": "GitHub", "url": "https://github.com"},
    {"name": "PyPI", "url": "https://pypi.org"},
]

TIMEOUT_SECONDS = 5


def _check(name: str, url: str) -> None:
    start = time.monotonic()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TaskEngine/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            status = resp.status
        elapsed_ms = int((time.monotonic() - start) * 1000)
        logging.info(f"Health check [{name}] {url} -> {status} ({elapsed_ms}ms)")
    except urllib.error.HTTPError as e:
        logging.warning(f"Health check [{name}] {url} -> HTTP {e.code}")
    except Exception as e:
        logging.error(f"Health check [{name}] {url} -> FAILED: {e}")


def run_health_check():
    logging.info(f"Health check task started — checking {len(ENDPOINTS)} endpoint(s)")
    for ep in ENDPOINTS:
        _check(ep["name"], ep["url"])
    logging.info("Health check task completed")
