"""Self-description types for capabilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class OperationDescriptor:
    """Describes a single capability operation."""

    name: str
    description: str
    inputs: dict[str, str]
    outputs: dict[str, str]


@dataclass(frozen=True)
class CapabilityDescriptor:
    """Self-description metadata for a capability."""

    name: str
    domain: str
    description: str
    deterministic: bool
    side_effects: str
    typical_latency: str
    network_required: bool
    operations: tuple[OperationDescriptor, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)
