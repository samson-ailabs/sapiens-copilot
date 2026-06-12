# SPDX-License-Identifier: Apache-2.0
"""Tests for the Settings configuration object."""

from pathlib import Path

import pytest

from sapiens.config import Settings


def test_from_env_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        Settings.from_env()


def test_from_env_reads_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    monkeypatch.setenv("SAPIENS_MODEL", "openai/gpt-4o")
    monkeypatch.setenv("SAPIENS_DB_PATH", "/tmp/sapiens-test.db")
    monkeypatch.setenv("SAPIENS_TEMPERATURE", "0.5")

    settings = Settings.from_env()

    assert settings.openrouter_api_key == "sk-test"
    assert settings.model == "openai/gpt-4o"
    assert settings.db_path == Path("/tmp/sapiens-test.db")
    assert settings.temperature == 0.5
