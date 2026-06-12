# SPDX-License-Identifier: Apache-2.0
"""Process-wide registry of the tools the agent exposes."""

from __future__ import annotations

from langchain_core.tools import BaseTool

_REGISTRY: list[BaseTool] = []


def register(tool: BaseTool) -> BaseTool:
    """Register a tool so the agent exposes it; returns it for use as a decorator."""
    _REGISTRY.append(tool)
    return tool


def get_tools() -> list[BaseTool]:
    """Return a snapshot of the registered tools."""
    return list(_REGISTRY)


def clear_registry() -> None:
    """Drop all registered tools. Primarily for test isolation."""
    _REGISTRY.clear()
