"""Factory helpers for selecting a git capability implementation."""

from __future__ import annotations

from pathlib import Path

from pegaso.capabilities.git.contract import Git
from pegaso.capabilities.git.local import LocalGitCapability
from pegaso.capabilities.git.mcp import McpGitCapability


def _mcp_available() -> bool:
    try:
        import mcp  # noqa: F401
        import mcp_server_git  # noqa: F401
    except ImportError:
        return False
    return True


def create_git_capability(
    repo_path: str | Path | None = None,
    *,
    prefer_mcp: bool = True,
) -> Git:
    """Create a git capability, preferring MCP when available."""

    if prefer_mcp and _mcp_available():
        return McpGitCapability(repo_path)
    return LocalGitCapability(repo_path)
