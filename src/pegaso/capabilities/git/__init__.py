"""Git capability package and module-level convenience API."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pegaso.capabilities.git.contract import Git
from pegaso.capabilities.git.descriptor import GIT_DESCRIPTOR
from pegaso.capabilities.git.factory import create_git_capability
from pegaso.capabilities.git.local import LocalGitCapability
from pegaso.capabilities.git.mcp import McpGitCapability

_default: Git | None = None


def configure(
    repo_path: str | Path | None = None,
    *,
    prefer_mcp: bool = True,
) -> Git:
    """Configure the module-level default git capability."""

    global _default
    _default = create_git_capability(repo_path, prefer_mcp=prefer_mcp)
    return _default


def _get_default() -> Git:
    global _default
    if _default is None:
        _default = create_git_capability(Path.cwd(), prefer_mcp=True)
    return _default


def status() -> dict[str, str]:
    return _get_default().status()


def diff(
    *,
    staged: bool = False,
    target: str | None = None,
    context_lines: int = 3,
) -> dict[str, str]:
    return _get_default().diff(
        staged=staged,
        target=target,
        context_lines=context_lines,
    )


def add(files: list[str]) -> dict[str, Any]:
    return _get_default().add(files)


def commit(message: str) -> dict[str, Any]:
    return _get_default().commit(message)


def checkout(branch: str) -> dict[str, Any]:
    return _get_default().checkout(branch)


def branch(
    name: str | None = None,
    *,
    create: bool = False,
    base_branch: str | None = None,
    branch_type: str = "local",
) -> dict[str, Any]:
    return _get_default().branch(
        name,
        create=create,
        base_branch=base_branch,
        branch_type=branch_type,
    )


def log(
    max_count: int = 10,
    *,
    start_timestamp: str | None = None,
    end_timestamp: str | None = None,
) -> dict[str, Any]:
    return _get_default().log(
        max_count,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
    )


def show(revision: str = "HEAD") -> dict[str, str]:
    return _get_default().show(revision)


def pull(
    remote: str = "origin",
    branch: str | None = None,
) -> dict[str, Any]:
    return _get_default().pull(remote=remote, branch=branch)


def push(
    remote: str = "origin",
    branch: str | None = None,
) -> dict[str, Any]:
    return _get_default().push(remote=remote, branch=branch)


def clone(url: str, destination: str) -> dict[str, Any]:
    return _get_default().clone(url=url, destination=destination)


__all__ = [
    "GIT_DESCRIPTOR",
    "Git",
    "LocalGitCapability",
    "McpGitCapability",
    "add",
    "branch",
    "checkout",
    "clone",
    "commit",
    "configure",
    "create_git_capability",
    "diff",
    "log",
    "pull",
    "push",
    "show",
    "status",
]
