"""PEGASO — a capability library for intelligent systems."""

from pegaso.core.capability import Capability
from pegaso.core.descriptor import CapabilityDescriptor, OperationDescriptor
from pegaso.core.registry import CapabilityRegistry
from pegaso.capabilities.git import LocalGitCapability
from pegaso.capabilities.local_files import LocalFilesCapability

__all__ = [
    "Capability",
    "CapabilityDescriptor",
    "CapabilityRegistry",
    "LocalFilesCapability",
    "LocalGitCapability",
    "OperationDescriptor",
]

__version__ = "0.1.0"
