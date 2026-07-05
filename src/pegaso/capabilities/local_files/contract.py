"""Public contract for the local_files capability."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LocalFiles(Protocol):
    """Filesystem capability contract."""

    def list_directory(self, path: str) -> dict[str, list[str]]:
        """Return directories and files at the given path."""

    def read_file(self, path: str) -> dict[str, Any]:
        """Read file contents with encoding and size metadata."""

    def write_file(
        self,
        path: str,
        content: str,
        overwrite: bool = True,
    ) -> dict[str, bool]:
        """Write content to a file."""

    def create_directory(self, path: str) -> dict[str, bool]:
        """Create a directory (including parents)."""

    def delete(self, path: str) -> dict[str, bool]:
        """Delete a file or directory."""

    def copy(self, source: str, destination: str) -> dict[str, bool]:
        """Copy a file or directory."""

    def move(self, source: str, destination: str) -> dict[str, bool]:
        """Move a file or directory."""

    def search(
        self,
        root: str,
        pattern: str,
        recursive: bool = True,
    ) -> dict[str, list[str]]:
        """Search files by name pattern."""

    def grep(
        self,
        root: str,
        query: str,
        recursive: bool = True,
    ) -> dict[str, list[Any]]:
        """Search inside file contents."""

    def stat(self, path: str) -> dict[str, Any]:
        """Return metadata for a filesystem object."""
