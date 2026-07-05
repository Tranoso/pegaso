"""Local Google Cloud SDK implementation of the BigQuery capability."""

from __future__ import annotations

from typing import Any

from pegaso.capabilities.bigquery._serialization import (
    serialize_row,
    serialize_schema_field,
    serialize_value,
)
from pegaso.capabilities.bigquery.descriptor import BIGQUERY_DESCRIPTOR
from pegaso.core.descriptor import CapabilityDescriptor
from pegaso.core.errors import CapabilityError


class LocalBigQueryCapability:
    """BigQuery capability backed by the official Google Cloud Python SDK."""

    def __init__(
        self,
        project: str | None = None,
        *,
        location: str | None = None,
    ) -> None:
        self._project = project
        self._location = location
        self._client = None

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
                "backend": "google-cloud-bigquery",
            },
        )

    @property
    def project(self) -> str:
        return self._project or self._get_client().project

    def execute_query(
        self,
        query: str,
        *,
        parameters: dict[str, Any] | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        if not query.strip():
            raise CapabilityError("Query cannot be empty")

        from google.cloud import bigquery

        client = self._get_client()
        job_config = bigquery.QueryJobConfig(
            dry_run=dry_run,
            query_parameters=_build_query_parameters(parameters),
        )
        job = client.query(query, job_config=job_config, location=self._location)
        if dry_run:
            return {
                "rows": [],
                "schema": [],
                "total_rows": 0,
                "job_id": job.job_id,
                "bytes_processed": job.total_bytes_processed,
            }

        result = job.result()
        schema = [serialize_schema_field(field) for field in result.schema]
        rows = [serialize_row(row) for row in result]
        return {
            "rows": rows,
            "schema": schema,
            "total_rows": result.total_rows,
            "job_id": job.job_id,
        }

    def execute_script(
        self,
        script: str,
        *,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not script.strip():
            raise CapabilityError("Script cannot be empty")

        from google.cloud import bigquery

        client = self._get_client()
        job_config = bigquery.QueryJobConfig(
            query_parameters=_build_query_parameters(parameters),
        )
        job = client.query(script, job_config=job_config, location=self._location)
        job.result()
        return {"job_id": job.job_id, "success": True}

    def get_job(self, job_id: str) -> dict[str, Any]:
        if not job_id.strip():
            raise CapabilityError("Job ID cannot be empty")

        job = self._get_client().get_job(job_id, location=self._location)
        return _serialize_job(job)

    def list_datasets(self, *, project: str | None = None) -> dict[str, Any]:
        client = self._get_client()
        datasets = [
            dataset.dataset_id
            for dataset in client.list_datasets(project=project or self.project)
        ]
        return {"datasets": datasets}

    def list_tables(
        self,
        dataset_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        if not dataset_id.strip():
            raise CapabilityError("Dataset ID cannot be empty")

        client = self._get_client()
        dataset_ref = f"{project or self.project}.{dataset_id}"
        tables = [
            table.table_id for table in client.list_tables(dataset_ref)
        ]
        return {"tables": tables}

    def get_table(
        self,
        dataset_id: str,
        table_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        table = self._get_table(dataset_id, table_id, project=project)
        return {
            "dataset_id": table.dataset_id,
            "table_id": table.table_id,
            "table_type": table.table_type,
            "num_rows": table.num_rows,
            "description": table.description or "",
        }

    def get_schema(
        self,
        dataset_id: str,
        table_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        table = self._get_table(dataset_id, table_id, project=project)
        fields = [serialize_schema_field(field) for field in table.schema]
        return {"fields": fields}

    def create_dataset(
        self,
        dataset_id: str,
        *,
        project: str | None = None,
        location: str | None = None,
    ) -> dict[str, Any]:
        if not dataset_id.strip():
            raise CapabilityError("Dataset ID cannot be empty")

        from google.cloud import bigquery

        client = self._get_client()
        dataset = bigquery.Dataset(f"{project or self.project}.{dataset_id}")
        if location or self._location:
            dataset.location = location or self._location
        client.create_dataset(dataset)
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

        from google.cloud import bigquery

        client = self._get_client()
        table_ref = f"{project or self.project}.{dataset_id}.{table_id}"
        table = bigquery.Table(
            table_ref,
            schema=[
                bigquery.SchemaField(
                    name=field["name"],
                    field_type=field["type"],
                    mode=field.get("mode", "NULLABLE"),
                    description=field.get("description", ""),
                )
                for field in schema
            ],
        )
        client.create_table(table)
        return {"success": True, "table_id": table_id}

    def delete_table(
        self,
        dataset_id: str,
        table_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        if not dataset_id.strip():
            raise CapabilityError("Dataset ID cannot be empty")
        if not table_id.strip():
            raise CapabilityError("Table ID cannot be empty")

        table_ref = f"{project or self.project}.{dataset_id}.{table_id}"
        self._get_client().delete_table(table_ref, not_found_ok=False)
        return {"success": True}

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                from google.cloud import bigquery
            except ImportError as exc:
                raise CapabilityError(
                    "The 'google-cloud-bigquery' package is required for the "
                    "local BigQuery capability. Install with: "
                    "pip install 'pegaso[bigquery]'"
                ) from exc

            self._client = bigquery.Client(
                project=self._project,
                location=self._location,
            )
        return self._client

    def _get_table(
        self,
        dataset_id: str,
        table_id: str,
        *,
        project: str | None = None,
    ) -> Any:
        if not dataset_id.strip():
            raise CapabilityError("Dataset ID cannot be empty")
        if not table_id.strip():
            raise CapabilityError("Table ID cannot be empty")

        table_ref = f"{project or self.project}.{dataset_id}.{table_id}"
        try:
            return self._get_client().get_table(table_ref)
        except Exception as exc:
            raise CapabilityError(
                f"Failed to get table '{table_ref}': {exc}"
            ) from exc


def _build_query_parameters(
    parameters: dict[str, Any] | None,
) -> list[Any]:
    if not parameters:
        return []

    from google.cloud import bigquery

    query_parameters: list[Any] = []
    for name, value in parameters.items():
        if isinstance(value, bool):
            param_type = "BOOL"
        elif isinstance(value, int):
            param_type = "INT64"
        elif isinstance(value, float):
            param_type = "FLOAT64"
        else:
            param_type = "STRING"
            value = serialize_value(value)
        query_parameters.append(
            bigquery.ScalarQueryParameter(name, param_type, value)
        )
    return query_parameters


def _serialize_job(job: Any) -> dict[str, Any]:
    errors = [error["message"] for error in (job.errors or [])]
    created = job.created.isoformat() if job.created else ""
    ended = job.ended.isoformat() if job.ended else None
    return {
        "job_id": job.job_id,
        "state": job.state,
        "errors": errors,
        "created": created,
        "ended": ended,
    }
