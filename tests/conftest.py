"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from pegaso.capabilities.local_files import LocalFilesCapability


@pytest.fixture
def sandbox(tmp_path: Path) -> LocalFilesCapability:
    """Create a local_files capability scoped to a temp directory."""
    return LocalFilesCapability(allowed_roots=[tmp_path])
