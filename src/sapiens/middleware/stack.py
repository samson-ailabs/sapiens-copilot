# SPDX-License-Identifier: Apache-2.0
"""Assembles the ordered middleware stack the agent runs with."""

from __future__ import annotations

from typing import Any

from langchain.agents.middleware import AgentMiddleware

from sapiens.middleware.patch import PatchToolCallsMiddleware


def build_middleware() -> list[AgentMiddleware[Any, Any, Any]]:
    """Return the ordered middleware stack applied to the agent.

    Order matters: later modules append their own middleware here.
    """
    return [PatchToolCallsMiddleware()]
