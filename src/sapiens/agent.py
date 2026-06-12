# SPDX-License-Identifier: Apache-2.0
"""The Sapiens agent kernel: build the agent and open its persistence."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.state import CompiledStateGraph

from sapiens.config import Settings
from sapiens.models import build_model
from sapiens.tools import get_tools

# Treated as an opaque runnable, so the four generic params are widened to Any.
Agent = CompiledStateGraph[Any, Any, Any, Any]


@contextmanager
def open_checkpointer(db_path: Path) -> Iterator[SqliteSaver]:
    """Open a persistent checkpointer at ``db_path``, closing it on exit."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with SqliteSaver.from_conn_string(str(db_path)) as saver:
        yield saver


def build_agent(
    settings: Settings | None = None,
    *,
    model: BaseChatModel | None = None,
    checkpointer: BaseCheckpointSaver[Any] | None = None,
) -> Agent:
    """Wire the model, tools, and persistence into a runnable agent.

    Args:
        settings: Runtime configuration; falls back to the environment.
        model: Language model to drive the agent; falls back to one from ``settings``.
        checkpointer: Where conversation history lives; falls back to memory-only.
    """
    settings = settings or Settings.from_env()
    model = model or build_model(settings)

    return create_agent(
        model=model,
        tools=get_tools(),
        system_prompt=settings.system_prompt,
        checkpointer=checkpointer or InMemorySaver(),
    )
