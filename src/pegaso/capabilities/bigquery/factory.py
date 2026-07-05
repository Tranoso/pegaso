"""Factory helpers for selecting a BigQuery capability implementation."""

from __future__ import annotations

from pegaso.capabilities.bigquery.contract import BigQuery
from pegaso.capabilities.bigquery.local import LocalBigQueryCapability
from pegaso.capabilities.bigquery.mcp import McpBigQueryCapability
from pegaso.capabilities.bigquery.mock import MockBigQueryCapability


def _mcp_available() -> bool:
    try:
        import mcp  # noqa: F401
        import mcp_server_bigquery  # noqa: F401
    except ImportError:
        return False
    return True


def create_bigquery_capability(
    project: str | None = None,
    *,
    location: str | None = None,
    prefer_mcp: bool = True,
    use_mock: bool = False,
) -> BigQuery:
    """Create a BigQuery capability, preferring MCP when available."""

    if use_mock:
        return MockBigQueryCapability(project or "mock-project")

    if prefer_mcp and _mcp_available():
        if not project:
            raise ValueError("project is required when prefer_mcp=True")
        if not location:
            raise ValueError("location is required when prefer_mcp=True")
        return McpBigQueryCapability(project, location=location)

    return LocalBigQueryCapability(project, location=location)
