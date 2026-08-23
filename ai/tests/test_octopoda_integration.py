"""Tests for the local-first Octopoda integration."""

from __future__ import annotations

import sys
from types import SimpleNamespace

import integration.octopoda as octopoda_integration


class FakeOctopoda:
    """Small stand-in that verifies arguments without opening a network connection."""

    created_with: list[tuple[str, str]] = []

    def __init__(self, *, api_key: str, base_url: str) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.agent_ids: list[str] = []
        self.created_with.append((api_key, base_url))

    def agent(self, agent_id: str) -> dict[str, str]:
        self.agent_ids.append(agent_id)
        return {"agent_id": agent_id}


def _install_fake_octopoda(monkeypatch) -> None:
    FakeOctopoda.created_with.clear()
    monkeypatch.setitem(sys.modules, "octopoda", SimpleNamespace(Octopoda=FakeOctopoda))
    monkeypatch.setattr(octopoda_integration, "_memory", None)


def test_uses_local_defaults_when_environment_is_not_set(monkeypatch) -> None:
    _install_fake_octopoda(monkeypatch)
    monkeypatch.delenv("OCTOPODA_API_KEY", raising=False)
    monkeypatch.delenv("OCTOPODA_BASE_URL", raising=False)

    memory = octopoda_integration.create_octopoda_memory()

    assert memory.api_key == "local-dev"
    assert memory.base_url == "http://localhost:8741"


def test_empty_environment_values_still_use_local_defaults(monkeypatch) -> None:
    _install_fake_octopoda(monkeypatch)
    monkeypatch.setenv("OCTOPODA_API_KEY", "")
    monkeypatch.setenv("OCTOPODA_BASE_URL", "")

    memory = octopoda_integration.create_octopoda_memory()

    assert memory.api_key == "local-dev"
    assert memory.base_url == "http://localhost:8741"


def test_brain_uses_configured_agent_and_cached_memory(monkeypatch) -> None:
    _install_fake_octopoda(monkeypatch)
    monkeypatch.setenv("OCTOPODA_API_KEY", "development-key")
    monkeypatch.setenv("OCTOPODA_BASE_URL", "http://127.0.0.1:8741")
    monkeypatch.setenv("OCTOPODA_AGENT_ID", "ucust-assistant")

    brain = octopoda_integration.get_octopoda_brain()
    same_memory = octopoda_integration.get_octopoda_memory()

    assert brain == {"agent_id": "ucust-assistant"}
    assert same_memory.api_key == "development-key"
    assert same_memory.base_url == "http://127.0.0.1:8741"
    assert FakeOctopoda.created_with == [("development-key", "http://127.0.0.1:8741")]
