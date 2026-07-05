"""MCP-backed implementation of the BigQuery capability."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any

from pegaso.capabilities.bigquery.descriptor import BIGQUERY_DESCRIPTOR
from pegaso.capabilities.bigquery.local import LocalBigQueryCapability
from pegaso.core.descriptor import CapabilityDescriptor
from pegaso.core.errors import CapabilityError
from pegaso.core.mcp_client import McpServerConfig, call_mcp_tool


class McpBigQueryCapability:
    """BigQuery capability that delegates to mcp-server-bigquery when possible."""

    def __init__(
        self,
        project: str,
        *,
        location: str,
        datasets: list[str] | None = None,
        server_command: str | None = None,
        server_args: tuple[str, ...] | None = None,
    ) -> None:
        if not project.strip():
            raise CapabilityError("Project ID is required for MCP BigQuery")
        if not location.strip():
            raise CapabilityError("Location is required for MCP BigQuery")

        self._project = project
        self._location = location
        self._local = LocalBigQueryCapability(project, location=location)
        env = {
            "BIGQUERY_PROJECT": project,
            "BIGQUERY_LOCATION": location,
        }
        if datasets:
            env["BIGQUERY_DATASETS"] = ",".join(datasets)

        if server_args is None:
            server_args = ("-m", "mcp_server_bigquery")
        self._server = McpServerConfig(
            command=server_command or sys.executable,
            args=server_args,
            env={**os.environ, **env},
        )

    @property
    def descriptor(self) -> CapabilityDescriptor:
        descriptor = BIGQUERY_DESCRIPTOR
        return CapabilityDescriptor(
            name=descriptor.name,
            domain=descriptor.domain,
            description=descriptor.description,
            deterministic=descriptor.deterministic,
            side_effects=descriptor.side_effects,
            typical_latency=descriptor.typical_latency,
            network_required=True,
            operations=descriptor.operations,
            metadata={
                **descriptor.metadata,
                "backend": "mcp-server-bigquery",
            },
        )

    @property
    def project(self) -> str:
        return self._project

    def execute_query(
        self,
        query: str,
        *,
        parameters: dict[str, Any] | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        if parameters or dry_run:
            return self._local.execute_query(
                query,
                parameters=parameters,
                dry_run=dry_run,
            )

        output = self._call_mcp("execute-query", {"query": query})
        rows = _parse_query_results(output)
        schema = _infer_schema(rows)
        return {
            "rows": rows,
            "schema": schema,
            "total_rows": len(rows),
            "job_id": "",
        }

    def execute_script(
        self,
        script: str,
        *,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._local.execute_script(script, parameters=parameters)

    def get_job(self, job_id: str) -> dict[str, Any]:
        return self._local.get_job(job_id)

    def list_datasets(self, *, project: str | None = None) -> dict[str, Any]:
        return self._local.list_datasets(project=project)

    def list_tables(
        self,
        dataset_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        if not dataset_id.strip():
            raise CapabilityError("Dataset ID cannot be empty")

        output = self._call_mcp("list-tables", {})
        tables = _parse_table_list(output, dataset_id)
        return {"tables": tables}

    def get_table(
        self,
        dataset_id: str,
        table_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        return self._local.get_table(
            dataset_id,
            table_id,
            project=project,
        )

    def get_schema(
        self,
        dataset_id: str,
        table_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        table_name = f"{dataset_id}.{table_id}"
        output = self._call_mcp("describe-table", {"table_name": table_name})
        fields = _parse_schema_from_ddl(output)
        return {"fields": fields}

    def create_dataset(
        self,
        dataset_id: str,
        *,
        project: str | None = None,
        location: str | None = None,
    ) -> dict[str, Any]:
        return self._local.create_dataset(
            dataset_id,
            project=project,
            location=location,
        )

    def create_table(
        self,
        dataset_id: str,
        table_id: str,
        schema: list[dict[str, str]],
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        return self._local.create_table(
            dataset_id,
            table_id,
            schema,
            project=project,
        )

    def delete_table(
        self,
        dataset_id: str,
        table_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        return self._local.delete_table(
            dataset_id,
            table_id,
            project=project,
        )

    def _call_mcp(self, tool_name: str, arguments: dict[str, Any]) -> str:
        try:
            return call_mcp_tool(self._server, tool_name, arguments)
        except ImportError:
            raise
        except Exception as exc:
            raise CapabilityError(
                f"MCP BigQuery tool '{tool_name}' failed: {exc}"
            ) from exc


def _parse_query_results(output: str) -> list[dict[str, Any]]:
    cleaned = output.strip()
    if not cleaned:
        return []

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return []

    if isinstance(parsed, list):
        return [row for row in parsed if isinstance(row, dict)]
    return []


def _infer_schema(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    if not rows:
        return []

    first = rows[0]
    return [
        {
            "name": name,
            "type": _infer_field_type(value),
            "mode": "NULLABLE",
            "description": "",
        }
        for name, value in first.items()
    ]


def _infer_field_type(value: Any) -> str:
    if isinstance(value, bool):
        return "BOOL"
    if isinstance(value, int):
        return "INT64"
    if isinstance(value, float):
        return "FLOAT64"
    return "STRING"


def _parse_table_list(output: str, dataset_id: str) -> list[str]:
    tables: list[str] = []
    prefix = f"{dataset_id}."
    for line in output.splitlines():
        cleaned = line.strip().strip("-").strip()
        if not cleaned:
            continue
        if cleaned.startswith(prefix):
            tables.append(cleaned.removeprefix(prefix))
        elif "." not in cleaned and cleaned:
            tables.append(cleaned)
    return sorted(set(tables))


def _parse_schema_from_ddl(ddl: str) -> list[dict[str, str]]:
    fields: list[dict[str, str]] = []
    for line in ddl.splitlines():
        match = re.match(
            r"\s*`?([A-Za-z_][A-Za-z0-9_]*)`?\s+([A-Z0-9]+)",
            line.strip().rstrip(","),
        )
        if not match:
            continue
        name, field_type = match.groups()
        fields.append(
            {
                "name": name,
                "type": field_type,
                "mode": "NULLABLE",
                "description": "",
            }
        )
    return fields
