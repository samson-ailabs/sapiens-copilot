# SPDX-License-Identifier: Apache-2.0
"""Smoke test: the package is importable. Real tests arrive with M1."""

import sapiens


def test_package_imports() -> None:
    assert sapiens.__doc__ is not None
