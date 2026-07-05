"""PEGASO capabilities."""

from pegaso.capabilities.bigquery import (
    BIGQUERY_DESCRIPTOR,
    BigQuery,
    LocalBigQueryCapability,
    McpBigQueryCapability,
    MockBigQueryCapability,
    create_bigquery_capability,
)
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
    "BIGQUERY_DESCRIPTOR",
    "BigQuery",
    "GIT_DESCRIPTOR",
    "Git",
    "LocalBigQueryCapability",
    "LocalFiles",
    "LocalFilesCapability",
    "LocalGitCapability",
    "McpBigQueryCapability",
    "McpGitCapability",
    "MockBigQueryCapability",
    "create_bigquery_capability",
    "create_git_capability",
]
