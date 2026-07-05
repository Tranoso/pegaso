"""Public contract for the git capability."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Git(Protocol):
    """Git capability contract."""

    def status(self) -> dict[str, str]:
        """Return the working tree status."""

    def diff(
        self,
        *,
        staged: bool = False,
        target: str | None = None,
        context_lines: int = 3,
    ) -> dict[str, str]:
        """Return a diff of unstaged, staged, or target changes."""

    def add(self, files: list[str]) -> dict[str, Any]:
        """Stage files for commit."""

    def commit(self, message: str) -> dict[str, Any]:
        """Create a commit with the given message."""

    def checkout(self, branch: str) -> dict[str, Any]:
        """Switch to the given branch."""

    def branch(
        self,
        name: str | None = None,
        *,
        create: bool = False,
        base_branch: str | None = None,
        branch_type: str = "local",
    ) -> dict[str, Any]:
        """List branches or create a new branch."""

    def log(
        self,
        max_count: int = 10,
        *,
        start_timestamp: str | None = None,
        end_timestamp: str | None = None,
    ) -> dict[str, Any]:
        """Return recent commit history."""

    def show(self, revision: str = "HEAD") -> dict[str, str]:
        """Show details for a revision."""

    def pull(
        self,
        remote: str = "origin",
        branch: str | None = None,
    ) -> dict[str, Any]:
        """Fetch and integrate changes from a remote."""

    def push(
        self,
        remote: str = "origin",
        branch: str | None = None,
    ) -> dict[str, Any]:
        """Publish local commits to a remote."""

    def clone(self, url: str, destination: str) -> dict[str, Any]:
        """Clone a repository into the destination path."""
