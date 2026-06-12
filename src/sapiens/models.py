# SPDX-License-Identifier: Apache-2.0
"""LLM wiring. Sapiens talks to models through OpenRouter."""

from __future__ import annotations

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from sapiens.config import Settings


def build_model(settings: Settings) -> BaseChatModel:
    """Build the chat model configured in ``settings``."""
    return init_chat_model(
        settings.model,
        model_provider="openrouter",
        temperature=settings.temperature,
        api_key=settings.openrouter_api_key,
    )
