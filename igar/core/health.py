"""Aggregate health check endpoint for infrastructure dependencies."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime, timezone

import requests
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from redis import Redis

HEALTHCHECK_TOTAL_BUDGET_SECONDS = 0.9
HEALTHCHECK_NETWORK_TIMEOUT_SECONDS = 0.5


def _ms(start: float) -> int:
    return max(int((time.perf_counter() - start) * 1000), 0)


def _check_postgresql() -> dict[str, object]:
    start = time.perf_counter()
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    return {"status": "up", "latency_ms": _ms(start)}


def _check_redis() -> dict[str, object]:
    start = time.perf_counter()
    redis_url = getattr(settings, "REDIS_URL", None) or getattr(settings, "CELERY_BROKER_URL", "redis://redis:6379/0")
    Redis.from_url(
        redis_url,
        socket_connect_timeout=HEALTHCHECK_NETWORK_TIMEOUT_SECONDS,
        socket_timeout=HEALTHCHECK_NETWORK_TIMEOUT_SECONDS,
    ).ping()
    return {"status": "up", "latency_ms": _ms(start)}


def _check_http_service(url: str) -> dict[str, object]:
    start = time.perf_counter()
    response = requests.get(url, timeout=HEALTHCHECK_NETWORK_TIMEOUT_SECONDS)
    response.raise_for_status()
    return {"status": "up", "latency_ms": _ms(start)}


def _iso_utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def health_check_view(request):
    request_start = time.perf_counter()
    deadline = request_start + HEALTHCHECK_TOTAL_BUDGET_SECONDS

    services: dict[str, dict[str, object]] = {}
    minio_endpoint = getattr(settings, "MINIO_ENDPOINT", "http://minio:9000").rstrip("/")
    elasticsearch_url = getattr(settings, "ELASTICSEARCH_URL", "http://elasticsearch:9200").rstrip("/")

    checks = {
        "postgresql": _check_postgresql,
        "redis": _check_redis,
        "minio": lambda: _check_http_service(f"{minio_endpoint}/minio/health/live"),
        "elasticsearch": lambda: _check_http_service(f"{elasticsearch_url}/_cluster/health"),
    }

    overall_up = True

    executor = ThreadPoolExecutor(max_workers=len(checks))
    futures = {service_name: executor.submit(check_fn) for service_name, check_fn in checks.items()}

    try:
        for service_name, future in futures.items():
            remaining_budget = max(deadline - time.perf_counter(), 0.0)

            if remaining_budget <= 0:
                overall_up = False
                services[service_name] = {"status": "down", "latency_ms": 0, "reason": "budget_exceeded"}
                continue

            try:
                services[service_name] = future.result(timeout=remaining_budget)
            except TimeoutError:
                overall_up = False
                services[service_name] = {"status": "down", "latency_ms": 0, "reason": "timeout"}
            except Exception:
                overall_up = False
                services[service_name] = {"status": "down", "latency_ms": 0}
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

    payload = {
        "status": "healthy" if overall_up else "unhealthy",
        "timestamp": _iso_utc_now(),
        "services": services,
    }

    return JsonResponse(payload, status=200 if overall_up else 503)
