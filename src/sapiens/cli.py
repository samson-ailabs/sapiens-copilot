# SPDX-License-Identifier: Apache-2.0
"""Interactive REPL for the agent - a development convenience, not the product."""

from __future__ import annotations

import uuid

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig

from sapiens.agent import Agent, build_agent, open_checkpointer
from sapiens.config import Settings

_BANNER = "Sapiens CLI - ask a question. Commands: /new (reset thread), /exit"
_USER_PROMPT = "\nyou > "
_ASSISTANT_PREFIX = "sapiens > "
_EXIT_COMMAND = "/exit"
_NEW_COMMAND = "/new"


def _new_thread_id() -> str:
    return str(uuid.uuid4())


class ChatSession:
    """Interactive session that streams replies from a single agent."""

    def __init__(self, agent: Agent) -> None:
        """Bind the session to ``agent`` and start a fresh thread."""
        self._agent = agent
        self._thread_id = _new_thread_id()

    def run(self) -> None:
        """Print the banner, then process input until the session ends."""
        print(_BANNER)
        while self._step():
            pass
        print("\nbye.")

    def _step(self) -> bool:
        """Read one line and route it. Return ``False`` to end the session."""
        try:
            user_input = input(_USER_PROMPT).strip()
        except (EOFError, KeyboardInterrupt):
            return False

        if not user_input:
            return True
        if user_input.startswith("/"):
            return self._handle_command(user_input)

        self._stream_reply(user_input)
        return True

    def _handle_command(self, command: str) -> bool:
        """Run a slash command. Return ``False`` to end the session."""
        if command == _EXIT_COMMAND:
            return False
        if command == _NEW_COMMAND:
            self._thread_id = _new_thread_id()
            print("(started a new conversation)")
            return True

        print(f"(unknown command: {command})")
        return True

    def _stream_reply(self, user_input: str) -> None:
        """Stream one assistant turn to stdout, token by token."""
        config: RunnableConfig = {"configurable": {"thread_id": self._thread_id}}
        try:
            events = self._agent.stream_events(
                {"messages": [{"role": "user", "content": user_input}]},
                version="v3",
                config=config,
            )

            print(_ASSISTANT_PREFIX, end="", flush=True)
            for message in events.messages:
                for delta in message.text:
                    print(delta, end="", flush=True)
            print()

        except KeyboardInterrupt:
            print("\n(interrupted)")
        except Exception as exc:  # one failed turn shouldn't end the session
            print(f"\n[error] {exc}")


def main() -> None:
    """Load configuration and run an interactive session."""
    load_dotenv()
    settings = Settings.from_env()

    with open_checkpointer(settings.db_path) as checkpointer:
        agent = build_agent(settings, checkpointer=checkpointer)
        ChatSession(agent).run()


if __name__ == "__main__":
    main()
