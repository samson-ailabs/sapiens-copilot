# SPDX-License-Identifier: Apache-2.0
"""Tests for the agent kernel: wiring, invocation, and SQLite persistence."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from sapiens.agent import build_agent, open_checkpointer
from sapiens.config import Settings
from sapiens.tools import clear_registry


@pytest.fixture(autouse=True)
def _clean_registry() -> Iterator[None]:
    clear_registry()
    yield
    clear_registry()


def _settings(tmp_path: Path) -> Settings:
    return Settings(openrouter_api_key="test-key", db_path=tmp_path / "threads.db")


def test_build_and_invoke_with_fake_model(tmp_path: Path) -> None:
    fake = GenericFakeChatModel(messages=iter([AIMessage(content="hi there")]))
    agent = build_agent(_settings(tmp_path), model=fake)  # default checkpointer

    result = agent.invoke(
        {"messages": [{"role": "user", "content": "hello"}]},
        config={"configurable": {"thread_id": "t1"}},
    )

    assert result["messages"][-1].content == "hi there"


def test_sqlite_persistence_across_turns(tmp_path: Path) -> None:
    fake = GenericFakeChatModel(
        messages=iter([AIMessage(content="one"), AIMessage(content="two")])
    )
    with open_checkpointer(tmp_path / "threads.db") as saver:
        agent = build_agent(_settings(tmp_path), model=fake, checkpointer=saver)
        config: RunnableConfig = {"configurable": {"thread_id": "conv"}}

        agent.invoke(
            {"messages": [{"role": "user", "content": "first"}]}, config=config
        )
        agent.invoke(
            {"messages": [{"role": "user", "content": "second"}]}, config=config
        )

        state = agent.get_state(config)
        # two user turns + two assistant replies, accumulated on one thread
        assert len(state.values["messages"]) == 4
