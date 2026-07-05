"""Tests for BigQuery capability operations."""

from __future__ import annotations

import pytest

from pegaso.capabilities.bigquery import (
    MockBigQueryCapability,
    create_bigquery_capability,
)
from pegaso.capabilities.bigquery.descriptor import BIGQUERY_DESCRIPTOR
from pegaso.capabilities.bigquery.local import LocalBigQueryCapability
from pegaso.core.errors import CapabilityError


@pytest.fixture
def bigquery() -> MockBigQueryCapability:
    capability = MockBigQueryCapability(project="test-project")
    capability.create_dataset("analytics", location="US")
    capability.create_table(
        "analytics",
        "events",
        [
            {"name": "event_id", "type": "STRING", "mode": "REQUIRED"},
            {"name": "value", "type": "INT64", "mode": "NULLABLE"},
        ],
    )
    capability.insert_rows(
        "analytics",
        "events",
        [
            {"event_id": "evt-1", "value": 10},
            {"event_id": "evt-2", "value": 20},
        ],
    )
    return capability


def test_descriptor_lists_required_operations():
    operation_names = {operation.name for operation in BIGQUERY_DESCRIPTOR.operations}
    assert operation_names == {
        "execute_query",
        "execute_script",
        "get_job",
        "list_datasets",
        "list_tables",
        "get_table",
        "get_schema",
        "create_dataset",
        "create_table",
        "delete_table",
    }


def test_execute_query_returns_rows(bigquery: MockBigQueryCapability):
    result = bigquery.execute_query(
        "SELECT * FROM analytics.events LIMIT 10"
    )
    assert result["total_rows"] == 2
    assert len(result["rows"]) == 2
    assert result["rows"][0]["event_id"] == "evt-1"
    assert result["job_id"]


def test_execute_query_dry_run(bigquery: MockBigQueryCapability):
    result = bigquery.execute_query(
        "SELECT * FROM analytics.events",
        dry_run=True,
    )
    assert result["rows"] == []
    assert result["total_rows"] == 0
    assert result["job_id"]


def test_execute_script_and_get_job(bigquery: MockBigQueryCapability):
    script_result = bigquery.execute_script("SELECT 1;")
    assert script_result["success"] is True

    job = bigquery.get_job(script_result["job_id"])
    assert job["state"] == "DONE"
    assert job["errors"] == []


def test_list_datasets_and_tables(bigquery: MockBigQueryCapability):
    datasets = bigquery.list_datasets()
    assert datasets["datasets"] == ["analytics"]

    tables = bigquery.list_tables("analytics")
    assert tables["tables"] == ["events"]


def test_get_table_and_schema(bigquery: MockBigQueryCapability):
    table = bigquery.get_table("analytics", "events")
    assert table["table_id"] == "events"
    assert table["num_rows"] == 2

    schema = bigquery.get_schema("analytics", "events")
    assert schema["fields"][0]["name"] == "event_id"
    assert schema["fields"][0]["type"] == "STRING"


def test_create_and_delete_table(bigquery: MockBigQueryCapability):
    schema = [{"name": "id", "type": "STRING", "mode": "REQUIRED"}]
    create_result = bigquery.create_table("analytics", "sessions", schema)
    assert create_result["success"] is True

    tables = bigquery.list_tables("analytics")
    assert "sessions" in tables["tables"]

    delete_result = bigquery.delete_table("analytics", "sessions")
    assert delete_result["success"] is True
    tables = bigquery.list_tables("analytics")
    assert "sessions" not in tables["tables"]


def test_create_dataset(bigquery: MockBigQueryCapability):
    result = bigquery.create_dataset("staging", location="EU")
    assert result["success"] is True
    assert "staging" in bigquery.list_datasets()["datasets"]


def test_execute_query_requires_query(bigquery: MockBigQueryCapability):
    with pytest.raises(CapabilityError, match="Query cannot be empty"):
        bigquery.execute_query("   ")


def test_create_bigquery_capability_uses_mock_when_requested():
    capability = create_bigquery_capability(use_mock=True)
    assert isinstance(capability, MockBigQueryCapability)


def test_create_bigquery_capability_falls_back_without_mcp(monkeypatch):
    monkeypatch.setattr(
        "pegaso.capabilities.bigquery.factory._mcp_available",
        lambda: False,
    )
    capability = create_bigquery_capability(
        "test-project",
        location="US",
        prefer_mcp=True,
    )
    assert isinstance(capability, LocalBigQueryCapability)


def test_module_level_api():
    from pegaso.capabilities import bigquery as bigquery_module

    bigquery_module.configure(project="test-project", use_mock=True)
    bigquery_module.create_dataset("analytics", location="US")
    bigquery_module.create_table(
        "analytics",
        "events",
        [{"name": "event_id", "type": "STRING", "mode": "REQUIRED"}],
    )

    result = bigquery_module.execute_query(
        "SELECT * FROM analytics.events LIMIT 1"
    )
    assert result["total_rows"] == 0

    datasets = bigquery_module.list_datasets()
    assert "analytics" in datasets["datasets"]
