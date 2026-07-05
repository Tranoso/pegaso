"""Core PEGASO framework types."""

from pegaso.core.capability import Capability
from pegaso.core.descriptor import CapabilityDescriptor, OperationDescriptor
from pegaso.core.errors import CapabilityError, PathAccessError
from pegaso.core.registry import CapabilityRegistry

__all__ = [
    "Capability",
    "CapabilityDescriptor",
    "CapabilityError",
    "CapabilityRegistry",
    "OperationDescriptor",
    "PathAccessError",
]
