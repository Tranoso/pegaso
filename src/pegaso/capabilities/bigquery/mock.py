"""In-memory mock implementation of the BigQuery capability for testing."""

from __future__ import annotations

import re
import uuid
from typing import Any

from pegaso.capabilities.bigquery.descriptor import BIGQUERY_DESCRIPTOR
from pegaso.core.descriptor import CapabilityDescriptor
from pegaso.core.errors import CapabilityError


class MockBigQueryCapability:
    """BigQuery capability backed by in-memory state."""

    def __init__(self, project: str = "mock-project") -> None:
        self._project = project
        self._datasets: dict[str, dict[str, Any]] = {}
        self._jobs: dict[str, dict[str, Any]] = {}

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
            network_required=False,
            operations=descriptor.operations,
            metadata={
                **descriptor.metadata,
                "backend": "mock",
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
        if not query.strip():
            raise CapabilityError("Query cannot be empty")

        job_id = _new_job_id()
        if dry_run:
            self._jobs[job_id] = _completed_job(job_id)
            return {
                "rows": [],
                "schema": [],
                "total_rows": 0,
                "job_id": job_id,
                "bytes_processed": 0,
            }

        rows, schema = self._evaluate_select(query, parameters or {})
        self._jobs[job_id] = _completed_job(job_id)
        return {
            "rows": rows,
            "schema": schema,
            "total_rows": len(rows),
            "job_id": job_id,
        }

    def execute_script(
        self,
        script: str,
        *,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not script.strip():
            raise CapabilityError("Script cannot be empty")

        job_id = _new_job_id()
        self._jobs[job_id] = _completed_job(job_id)
        return {"job_id": job_id, "success": True}

    def get_job(self, job_id: str) -> dict[str, Any]:
        if not job_id.strip():
            raise CapabilityError("Job ID cannot be empty")
        if job_id not in self._jobs:
            raise CapabilityError(f"Job not found: {job_id}")
        return dict(self._jobs[job_id])

    def list_datasets(self, *, project: str | None = None) -> dict[str, Any]:
        _assert_project(project or self._project, self._project)
        return {"datasets": sorted(self._datasets)}

    def list_tables(
        self,
        dataset_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        if not dataset_id.strip():
            raise CapabilityError("Dataset ID cannot be empty")
        _assert_project(project or self._project, self._project)
        dataset = self._require_dataset(dataset_id)
        return {"tables": sorted(dataset["tables"])}

    def get_table(
        self,
        dataset_id: str,
        table_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        table = self._require_table(dataset_id, table_id, project=project)
        return {
            "dataset_id": dataset_id,
            "table_id": table_id,
            "table_type": table["table_type"],
            "num_rows": len(table["rows"]),
            "description": table.get("description", ""),
        }

    def get_schema(
        self,
        dataset_id: str,
        table_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        table = self._require_table(dataset_id, table_id, project=project)
        return {"fields": list(table["schema"])}

    def create_dataset(
        self,
        dataset_id: str,
        *,
        project: str | None = None,
        location: str | None = None,
    ) -> dict[str, Any]:
        if not dataset_id.strip():
            raise CapabilityError("Dataset ID cannot be empty")
        _assert_project(project or self._project, self._project)
        if dataset_id in self._datasets:
            raise CapabilityError(f"Dataset already exists: {dataset_id}")
        self._datasets[dataset_id] = {
            "location": location or "US",
            "tables": {},
        }
        return {"success": True, "dataset_id": dataset_id}

    def create_table(
        self,
        dataset_id: str,
        table_id: str,
        schema: list[dict[str, str]],
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        if not dataset_id.strip():
            raise CapabilityError("Dataset ID cannot be empty")
        if not table_id.strip():
            raise CapabilityError("Table ID cannot be empty")
        if not schema:
            raise CapabilityError("Schema cannot be empty")

        dataset = self._require_dataset(dataset_id, project=project)
        if table_id in dataset["tables"]:
            raise CapabilityError(f"Table already exists: {table_id}")

        dataset["tables"][table_id] = {
            "schema": list(schema),
            "rows": [],
            "table_type": "TABLE",
            "description": "",
        }
        return {"success": True, "table_id": table_id}

    def delete_table(
        self,
        dataset_id: str,
        table_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        dataset = self._require_dataset(dataset_id, project=project)
        if table_id not in dataset["tables"]:
            raise CapabilityError(f"Table not found: {table_id}")
        del dataset["tables"][table_id]
        return {"success": True}

    def insert_rows(
        self,
        dataset_id: str,
        table_id: str,
        rows: list[dict[str, Any]],
    ) -> None:
        table = self._require_table(dataset_id, table_id)
        table["rows"].extend(rows)

    def _require_dataset(
        self,
        dataset_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        _assert_project(project or self._project, self._project)
        if dataset_id not in self._datasets:
            raise CapabilityError(f"Dataset not found: {dataset_id}")
        return self._datasets[dataset_id]

    def _require_table(
        self,
        dataset_id: str,
        table_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        dataset = self._require_dataset(dataset_id, project=project)
        if table_id not in dataset["tables"]:
            raise CapabilityError(f"Table not found: {table_id}")
        return dataset["tables"][table_id]

    def _evaluate_select(
        self,
        query: str,
        parameters: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        normalized = " ".join(query.strip().rstrip(";").split())
        match = re.match(
            r"(?i)select\s+\*\s+from\s+([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)"
            r"(?:\s+limit\s+(\d+))?$",
            normalized,
        )
        if not match:
            raise CapabilityError(
                "Mock BigQuery only supports simple SELECT * FROM dataset.table "
                "queries with an optional LIMIT clause."
            )

        dataset_id, table_id, limit_text = match.groups()
        table = self._require_table(dataset_id, table_id)
        rows = [dict(row) for row in table["rows"]]
        if limit_text is not None:
            rows = rows[: int(limit_text)]
        return rows, list(table["schema"])


def _new_job_id() -> str:
    return f"job_{uuid.uuid4().hex[:16]}"


def _completed_job(job_id: str) -> dict[str, Any]:
    return {
        "job_id": job_id,
        "state": "DONE",
        "errors": [],
        "created": "2026-01-01T00:00:00",
        "ended": "2026-01-01T00:00:01",
    }


def _assert_project(requested: str, configured: str) -> None:
    if requested != configured:
        raise CapabilityError(
            f"Project mismatch: expected '{configured}', got '{requested}'"
        )
