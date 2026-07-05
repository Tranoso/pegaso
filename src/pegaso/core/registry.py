"""Capability registration and lookup."""

from __future__ import annotations

from pegaso.core.capability import Capability
from pegaso.core.errors import CapabilityError


class CapabilityRegistry:
    """Register and resolve capabilities by name."""

    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}

    def register(self, capability: Capability) -> None:
        name = capability.descriptor.name
        if name in self._capabilities:
            raise CapabilityError(f"Capability already registered: {name}")
        self._capabilities[name] = capability

    def get(self, name: str) -> Capability:
        try:
            return self._capabilities[name]
        except KeyError as exc:
            raise CapabilityError(f"Capability not found: {name}") from exc

    def list_names(self) -> list[str]:
        return sorted(self._capabilities)
