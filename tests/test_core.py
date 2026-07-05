"""Tests for the core capability framework."""

import pytest

from pegaso.capabilities.local_files import LocalFilesCapability
from pegaso.core.registry import CapabilityRegistry
from pegaso.core.errors import CapabilityError


def test_capability_registry_register_and_get(tmp_path):
    registry = CapabilityRegistry()
    capability = LocalFilesCapability(allowed_roots=[tmp_path])

    registry.register(capability)
    assert registry.get("local_files") is capability
    assert registry.list_names() == ["local_files"]


def test_capability_registry_duplicate_raises(tmp_path):
    registry = CapabilityRegistry()
    capability = LocalFilesCapability(allowed_roots=[tmp_path])

    registry.register(capability)
    with pytest.raises(CapabilityError, match="already registered"):
        registry.register(capability)


def test_capability_registry_missing_raises():
    registry = CapabilityRegistry()
    with pytest.raises(CapabilityError, match="not found"):
        registry.get("local_files")


def test_local_files_descriptor(tmp_path):
    capability = LocalFilesCapability(allowed_roots=[tmp_path])
    descriptor = capability.descriptor

    assert descriptor.name == "local_files"
    assert descriptor.domain == "Filesystem"
    assert descriptor.deterministic is True
    assert descriptor.network_required is False
    assert len(descriptor.operations) == 10
    operation_names = {op.name for op in descriptor.operations}
    assert operation_names == {
        "list_directory",
        "read_file",
        "write_file",
        "create_directory",
        "delete",
        "copy",
        "move",
        "search",
        "grep",
        "stat",
    }
