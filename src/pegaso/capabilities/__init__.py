"""PEGASO capabilities."""

from pegaso.capabilities.git import (
    GIT_DESCRIPTOR,
    Git,
    LocalGitCapability,
    McpGitCapability,
    create_git_capability,
)
from pegaso.capabilities.local_files.contract import LocalFiles
from pegaso.capabilities.local_files.local import LocalFilesCapability

__all__ = [
    "GIT_DESCRIPTOR",
    "Git",
    "LocalFiles",
    "LocalFilesCapability",
    "LocalGitCapability",
    "McpGitCapability",
    "create_git_capability",
]
