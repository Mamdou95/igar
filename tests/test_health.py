from unittest.mock import patch

import pytest


@pytest.mark.django_db
def test_health_endpoint_returns_200_when_all_services_are_up(client):
    with patch("igar.core.health._check_postgresql", return_value={"status": "up", "latency_ms": 2}), patch(
        "igar.core.health._check_redis", return_value={"status": "up", "latency_ms": 1}
    ), patch("igar.core.health._check_http_service", return_value={"status": "up", "latency_ms": 5}):
        response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["services"]["postgresql"]["status"] == "up"
    assert payload["services"]["redis"]["status"] == "up"
    assert payload["services"]["minio"]["status"] == "up"
    assert payload["services"]["elasticsearch"]["status"] == "up"


@pytest.mark.django_db
def test_health_endpoint_returns_503_when_a_dependency_is_down(client):
    with patch("igar.core.health._check_postgresql", return_value={"status": "up", "latency_ms": 2}), patch(
        "igar.core.health._check_redis", side_effect=RuntimeError("redis down")
    ), patch("igar.core.health._check_http_service", return_value={"status": "up", "latency_ms": 5}):
        response = client.get("/health")

    assert response.status_code == 503
    payload = response.json()
    assert payload["status"] == "unhealthy"
    assert payload["services"]["redis"]["status"] == "down"
