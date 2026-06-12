# SPDX-License-Identifier: Apache-2.0
"""Tests for the middleware stack: composition and tool-call patching."""

from __future__ import annotations

from typing import Any, cast

from langchain.agents.middleware import AgentState
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Overwrite

from sapiens.middleware import PatchToolCallsMiddleware, build_middleware

_RUNTIME = cast(Runtime[Any], None)  # PatchToolCallsMiddleware ignores the runtime


def _ai_with_call(call_id: str) -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[{"name": "search", "args": {}, "id": call_id, "type": "tool_call"}],
    )


def test_build_middleware_includes_patch() -> None:
    stack = build_middleware()
    assert any(isinstance(m, PatchToolCallsMiddleware) for m in stack)


def test_patch_inserts_reply_for_dangling_call() -> None:
    state: AgentState[Any] = {"messages": [HumanMessage("hi"), _ai_with_call("call_1")]}

    result = PatchToolCallsMiddleware().before_agent(state, _RUNTIME)

    assert result is not None
    patched = result["messages"]
    assert isinstance(patched, Overwrite)
    replies = [m for m in patched.value if isinstance(m, ToolMessage)]
    assert [m.tool_call_id for m in replies] == ["call_1"]


def test_patch_is_noop_when_call_is_answered() -> None:
    state: AgentState[Any] = {
        "messages": [
            _ai_with_call("call_1"),
            ToolMessage(content="done", tool_call_id="call_1"),
        ]
    }

    assert PatchToolCallsMiddleware().before_agent(state, _RUNTIME) is None
