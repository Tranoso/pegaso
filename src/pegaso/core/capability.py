"""Base capability protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pegaso.core.descriptor import CapabilityDescriptor


@runtime_checkable
class Capability(Protocol):
    """Uniform interface every PEGASO capability implements."""

    @property
    def descriptor(self) -> CapabilityDescriptor:
        """Return self-description metadata for this capability."""
