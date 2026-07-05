"""Self-description for the BigQuery capability."""

from pegaso.core.descriptor import CapabilityDescriptor, OperationDescriptor

BIGQUERY_DESCRIPTOR = CapabilityDescriptor(
    name="bigquery",
    domain="Data Warehouse",
    description=(
        "Consistent interface for Google BigQuery operations. "
        "Implementation may be local SDK, MCP-backed, or mock."
    ),
    deterministic=False,
    side_effects="Common (DDL/DML operations mutate warehouse state)",
    typical_latency="Medium",
    network_required=True,
    metadata={"preferred_backend": "mcp-server-bigquery"},
    operations=(
        OperationDescriptor(
            name="execute_query",
            description="Executes a SQL query and returns rows.",
            inputs={
                "query": "SQL query text",
                "parameters": "Named query parameters (optional)",
                "dry_run": "Whether to validate without executing (optional)",
            },
            outputs={
                "rows": "Result rows as dictionaries",
                "schema": "Column schema definitions",
                "total_rows": "Number of rows returned",
                "job_id": "BigQuery job identifier",
            },
        ),
        OperationDescriptor(
            name="execute_script",
            description="Submits a multi-statement SQL script as a job.",
            inputs={
                "script": "SQL script text",
                "parameters": "Named query parameters (optional)",
            },
            outputs={
                "job_id": "BigQuery job identifier",
                "success": "Whether submission succeeded",
            },
        ),
        OperationDescriptor(
            name="get_job",
            description="Retrieves metadata for a BigQuery job.",
            inputs={"job_id": "BigQuery job identifier"},
            outputs={
                "job_id": "BigQuery job identifier",
                "state": "Job state",
                "errors": "Job error messages",
                "created": "Job creation timestamp",
                "ended": "Job completion timestamp when available",
            },
        ),
        OperationDescriptor(
            name="list_datasets",
            description="Lists datasets in a project.",
            inputs={"project": "GCP project ID (optional)"},
            outputs={"datasets": "Dataset identifiers"},
        ),
        OperationDescriptor(
            name="list_tables",
            description="Lists tables in a dataset.",
            inputs={
                "dataset_id": "Dataset identifier",
                "project": "GCP project ID (optional)",
            },
            outputs={"tables": "Table identifiers"},
        ),
        OperationDescriptor(
            name="get_table",
            description="Returns metadata for a table.",
            inputs={
                "dataset_id": "Dataset identifier",
                "table_id": "Table identifier",
                "project": "GCP project ID (optional)",
            },
            outputs={
                "dataset_id": "Dataset identifier",
                "table_id": "Table identifier",
                "table_type": "Table type",
                "num_rows": "Row count when available",
                "description": "Table description when available",
            },
        ),
        OperationDescriptor(
            name="get_schema",
            description="Returns the schema for a table.",
            inputs={
                "dataset_id": "Dataset identifier",
                "table_id": "Table identifier",
                "project": "GCP project ID (optional)",
            },
            outputs={"fields": "Schema field definitions"},
        ),
        OperationDescriptor(
            name="create_dataset",
            description="Creates a dataset.",
            inputs={
                "dataset_id": "Dataset identifier",
                "project": "GCP project ID (optional)",
                "location": "Dataset location (optional)",
            },
            outputs={
                "success": "Whether creation succeeded",
                "dataset_id": "Created dataset identifier",
            },
        ),
        OperationDescriptor(
            name="create_table",
            description="Creates a table with the given schema.",
            inputs={
                "dataset_id": "Dataset identifier",
                "table_id": "Table identifier",
                "schema": "Schema field definitions",
                "project": "GCP project ID (optional)",
            },
            outputs={
                "success": "Whether creation succeeded",
                "table_id": "Created table identifier",
            },
        ),
        OperationDescriptor(
            name="delete_table",
            description="Deletes a table.",
            inputs={
                "dataset_id": "Dataset identifier",
                "table_id": "Table identifier",
                "project": "GCP project ID (optional)",
            },
            outputs={"success": "Whether deletion succeeded"},
        ),
    ),
)
