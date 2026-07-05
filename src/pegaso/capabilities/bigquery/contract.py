"""Public contract for the BigQuery capability."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class BigQuery(Protocol):
    """BigQuery capability contract."""

    def execute_query(
        self,
        query: str,
        *,
        parameters: dict[str, Any] | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Execute a SQL query and return results."""

    def execute_script(
        self,
        script: str,
        *,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Submit a long-running SQL script as a BigQuery job."""

    def get_job(self, job_id: str) -> dict[str, Any]:
        """Retrieve metadata for a BigQuery job."""

    def list_datasets(self, *, project: str | None = None) -> dict[str, Any]:
        """List datasets in a project."""

    def list_tables(
        self,
        dataset_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        """List tables in a dataset."""

    def get_table(
        self,
        dataset_id: str,
        table_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        """Return metadata for a table."""

    def get_schema(
        self,
        dataset_id: str,
        table_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        """Return the schema for a table."""

    def create_dataset(
        self,
        dataset_id: str,
        *,
        project: str | None = None,
        location: str | None = None,
    ) -> dict[str, Any]:
        """Create a dataset."""

    def create_table(
        self,
        dataset_id: str,
        table_id: str,
        schema: list[dict[str, str]],
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        """Create a table with the given schema."""

    def delete_table(
        self,
        dataset_id: str,
        table_id: str,
        *,
        project: str | None = None,
    ) -> dict[str, Any]:
        """Delete a table."""
