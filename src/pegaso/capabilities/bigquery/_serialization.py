"""Helpers for serializing BigQuery values to JSON-friendly structures."""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any


def serialize_value(value: Any) -> Any:
    """Convert a BigQuery cell value into a JSON-friendly representation."""

    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, dict):
        return {key: serialize_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialize_value(item) for item in value]
    return str(value)


def serialize_schema_field(field: Any) -> dict[str, str]:
    """Convert a BigQuery schema field into a dictionary."""

    return {
        "name": field.name,
        "type": field.field_type,
        "mode": field.mode or "NULLABLE",
        "description": field.description or "",
    }


def serialize_row(row: Any) -> dict[str, Any]:
    """Convert a BigQuery row mapping into a dictionary."""

    return {key: serialize_value(value) for key, value in row.items()}
