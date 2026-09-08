"""
Integration and Unit tests for StudioSonar FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_healthcheck_endpoint():
    """Validates /healthz returns status healthy and expected agent team metadata."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "studiosonar" in data["service"]
    assert "gemini" in data["model"] and "flash" in data["model"]


def test_api_v1_health_endpoint():
    """Validates /api/v1/health returns detailed cluster health metadata."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "StudioSonarRootTaskmaster" in data["agents"]


def test_dashboard_ui_endpoint():
    """Validates root endpoint serves HTML dashboard with anti-cache headers."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "no-cache" in response.headers.get("cache-control", "")
    assert "StudioSonar" in response.text


def test_chat_command_endpoint_validation():
    """Validates settings copilot chat command endpoint."""
    response = client.post(
        "/api/v1/chat/command",
        json={"message": "quét 30 ngày"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
