"""Tests for serving Octopoda's bundled dashboard in local mode."""

from __future__ import annotations

from fastapi.testclient import TestClient

from integration.octopoda_dashboard import app


def test_dashboard_bootstraps_local_authentication(monkeypatch) -> None:
    monkeypatch.setenv("OCTOPODA_API_KEY", "local-test-key")

    response = TestClient(app).get("/dashboard")

    assert response.status_code == 200
    assert "octopoda_api_key" in response.text
    assert "local-test-key" in response.text


def test_dashboard_serves_react_assets() -> None:
    response = TestClient(app).get("/favicon.ico")

    assert response.status_code == 200
