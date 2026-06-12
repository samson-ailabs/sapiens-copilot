# SPDX-License-Identifier: Apache-2.0
"""Runtime configuration for the Sapiens agent kernel."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_MODEL = "anthropic/claude-sonnet-4-6"
DEFAULT_DB_PATH = "data/threads.db"
DEFAULT_SYSTEM_PROMPT = (
    "You are Sapiens, an embedded copilot inside an enterprise app. "
    "Be concise and accurate, cite your sources when you have them, "
    "and say so when you are unsure rather than guessing."
)


class Settings(BaseModel):
    """Immutable agent configuration; build it with :meth:`from_env`.

    Attributes:
        openrouter_api_key: Credential for the LLM gateway.
        model: Which model the agent should use.
        temperature: How varied responses are (0 = focused, 2 = creative).
        db_path: Where conversation history is stored.
        system_prompt: The agent's standing instructions.
    """

    model_config = ConfigDict(frozen=True)

    openrouter_api_key: str = Field(repr=False)
    model: str = DEFAULT_MODEL
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    db_path: Path = Path(DEFAULT_DB_PATH)
    system_prompt: str = DEFAULT_SYSTEM_PROMPT

    @classmethod
    def from_env(cls) -> Settings:
        """Build settings from environment variables.

        Raises:
            RuntimeError: If ``OPENROUTER_API_KEY`` is unset.
        """
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. Export it (or add it to a .env file) "
                "before starting Sapiens."
            )

        return cls(
            openrouter_api_key=api_key,
            model=os.environ.get("SAPIENS_MODEL", DEFAULT_MODEL),
            temperature=float(os.environ.get("SAPIENS_TEMPERATURE", "0.0")),
            db_path=Path(os.environ.get("SAPIENS_DB_PATH", DEFAULT_DB_PATH)),
        )
