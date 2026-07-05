"""BigQuery capability package and module-level convenience API."""

from __future__ import annotations

from typing import Any

from pegaso.capabilities.bigquery.contract import BigQuery
from pegaso.capabilities.bigquery.descriptor import BIGQUERY_DESCRIPTOR
from pegaso.capabilities.bigquery.factory import create_bigquery_capability
from pegaso.capabilities.bigquery.local import LocalBigQueryCapability
from pegaso.capabilities.bigquery.mcp import McpBigQueryCapability
from pegaso.capabilities.bigquery.mock import MockBigQueryCapability

_default: BigQuery | None = None


def configure(
    project: str | None = None,
    *,
    location: str | None = None,
    prefer_mcp: bool = False,
    use_mock: bool = False,
) -> BigQuery:
    """Configure the module-level default BigQuery capability."""

    global _default
    _default = create_bigquery_capability(
        project,
        location=location,
        prefer_mcp=prefer_mcp,
        use_mock=use_mock,
    )
    return _default


def _get_default() -> BigQuery:
    global _default
    if _default is None:
        _default = create_bigquery_capability(use_mock=True)
    return _default


def execute_query(
    query: str,
    *,
    parameters: dict[str, Any] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    return _get_default().execute_query(
        query,
        parameters=parameters,
        dry_run=dry_run,
    )


def execute_script(
    script: str,
    *,
    parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _get_default().execute_script(script, parameters=parameters)


def get_job(job_id: str) -> dict[str, Any]:
    return _get_default().get_job(job_id)


def list_datasets(*, project: str | None = None) -> dict[str, Any]:
    return _get_default().list_datasets(project=project)


def list_tables(
    dataset_id: str,
    *,
    project: str | None = None,
) -> dict[str, Any]:
    return _get_default().list_tables(dataset_id, project=project)


def get_table(
    dataset_id: str,
    table_id: str,
    *,
    project: str | None = None,
) -> dict[str, Any]:
    return _get_default().get_table(dataset_id, table_id, project=project)


def get_schema(
    dataset_id: str,
    table_id: str,
    *,
    project: str | None = None,
) -> dict[str, Any]:
    return _get_default().get_schema(dataset_id, table_id, project=project)


def create_dataset(
    dataset_id: str,
    *,
    project: str | None = None,
    location: str | None = None,
) -> dict[str, Any]:
    return _get_default().create_dataset(
        dataset_id,
        project=project,
        location=location,
    )


def create_table(
    dataset_id: str,
    table_id: str,
    schema: list[dict[str, str]],
    *,
    project: str | None = None,
) -> dict[str, Any]:
    return _get_default().create_table(
        dataset_id,
        table_id,
        schema,
        project=project,
    )


def delete_table(
    dataset_id: str,
    table_id: str,
    *,
    project: str | None = None,
) -> dict[str, Any]:
    return _get_default().delete_table(dataset_id, table_id, project=project)


__all__ = [
    "BIGQUERY_DESCRIPTOR",
    "BigQuery",
    "LocalBigQueryCapability",
    "McpBigQueryCapability",
    "MockBigQueryCapability",
    "configure",
    "create_bigquery_capability",
    "create_dataset",
    "create_table",
    "delete_table",
    "execute_query",
    "execute_script",
    "get_job",
    "get_schema",
    "get_table",
    "list_datasets",
    "list_tables",
]
