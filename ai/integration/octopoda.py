"""Local-first Octopoda client configuration for UCust.AI.

The Octopoda cloud client validates that an API key is present during
construction.  Supplying the local development key *and* an explicit local
base URL ensures that a missing cloud key never makes application start-up
fail with ``AuthError``.
"""

from __future__ import annotations

import os
from typing import Any, Optional


DEFAULT_API_KEY = "local-dev"
DEFAULT_BASE_URL = "http://localhost:8741"
DEFAULT_AGENT_ID = "my-assistant"

_memory: Optional[Any] = None


def create_octopoda_memory(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Any:
    """Create an Octopoda client configured for the local API server.

    Environment values are supported for deployments, while empty or missing
    values safely fall back to the local development configuration.
    """
    try:
        from octopoda import Octopoda
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Octopoda is not installed. Install project dependencies with "
            "`pip install -r requirements.txt`."
        ) from exc

    resolved_api_key = api_key or os.getenv("OCTOPODA_API_KEY") or DEFAULT_API_KEY
    resolved_base_url = base_url or os.getenv("OCTOPODA_BASE_URL") or DEFAULT_BASE_URL

    # Do not omit either parameter: Octopoda otherwise defaults to its cloud
    # endpoint and rejects a missing key with AuthError.
    return Octopoda(api_key=resolved_api_key, base_url=resolved_base_url)


def get_octopoda_memory() -> Any:
    """Return the process-wide local Octopoda client."""
    global _memory
    if _memory is None:
        _memory = create_octopoda_memory()
    return _memory


def get_octopoda_brain(agent_id: Optional[str] = None) -> Any:
    """Return the configured assistant memory handle.

    Calling this function registers/reconnects the agent with the server, so
    it is intentionally lazy: importing the FastAPI application does not
    require the local Octopoda server to be running yet.
    """
    resolved_agent_id = agent_id or os.getenv("OCTOPODA_AGENT_ID") or DEFAULT_AGENT_ID
    memory = get_octopoda_memory()
    brain = memory.agent(resolved_agent_id)
    return brain


__all__ = [
    "DEFAULT_AGENT_ID",
    "DEFAULT_API_KEY",
    "DEFAULT_BASE_URL",
    "create_octopoda_memory",
    "get_octopoda_brain",
    "get_octopoda_memory",
]
