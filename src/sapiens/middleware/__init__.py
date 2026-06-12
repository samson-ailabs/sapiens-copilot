# SPDX-License-Identifier: Apache-2.0
"""Middleware subsystem: the composable stack wrapping the agent loop."""

from __future__ import annotations

from sapiens.middleware.patch import PatchToolCallsMiddleware
from sapiens.middleware.stack import build_middleware

__all__ = ["PatchToolCallsMiddleware", "build_middleware"]
