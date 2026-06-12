# SPDX-License-Identifier: Apache-2.0
"""Middleware that repairs dangling tool calls in the message history."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from langchain.agents.middleware import AgentMiddleware, AgentState
from langchain_core.messages import AIMessage, AnyMessage, ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Overwrite


class PatchToolCallsMiddleware(AgentMiddleware[AgentState, Any, Any]):
    """Give every unanswered tool call a synthetic reply before the model runs."""

    def before_agent(
        self, state: AgentState, runtime: Runtime[Any]
    ) -> dict[str, Any] | None:
        """Repair dangling tool calls so the next model call sees a valid history.

        On resume (after an interrupt or crash) a tool call may have no reply, which
        providers reject; each unanswered call gets a synthetic reply in its place.
        """
        messages: list[AnyMessage] = state["messages"]
        answered = {m.tool_call_id for m in messages if isinstance(m, ToolMessage)}

        patched: list[AnyMessage] = []
        for message in messages:
            patched.append(message)
            if isinstance(message, AIMessage):
                patched.extend(_replies_for_unanswered(message, answered))

        if len(patched) == len(messages):
            return None

        return {"messages": Overwrite(patched)}


def _replies_for_unanswered(
    message: AIMessage, answered: set[str]
) -> Iterator[ToolMessage]:
    valid = ((call["name"], call["id"], False) for call in message.tool_calls)
    invalid = ((call["name"], call["id"], True) for call in message.invalid_tool_calls)

    for name, call_id, malformed in (*valid, *invalid):
        if call_id is not None and call_id not in answered:
            yield _synthetic_reply(name, call_id, malformed)


def _synthetic_reply(name: str | None, call_id: str, malformed: bool) -> ToolMessage:
    tool = name or "unknown"
    reason = (
        "its arguments were malformed or truncated"
        if malformed
        else "it was interrupted before completing"
    )

    return ToolMessage(
        content=f"Tool call {tool} ({call_id}) was not executed: {reason}.",
        name=tool,
        tool_call_id=call_id,
    )
