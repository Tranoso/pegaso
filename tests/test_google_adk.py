"""Tests for the Google ADK integration bridge."""

import inspect
from pathlib import Path

import pytest

from pegaso.capabilities.local_files import LocalFilesCapability
from pegaso.core.errors import CapabilityError
from pegaso.core.registry import CapabilityRegistry
from pegaso.integrations.google_adk import (
    capability_to_adk_tools,
    describe_capabilities,
    make_adk_tool,
    registry_to_adk_tools,
)


def test_make_adk_tool_name_and_signature(tmp_path: Path):
    capability = LocalFilesCapability(allowed_roots=[tmp_path])
    tool = make_adk_tool(capability, "read_file")

    assert tool.__name__ == "local_files_read_file"
    assert "path" in inspect.signature(tool).parameters
    assert tool.__doc__ is not None
    assert "path" in tool.__doc__


def test_make_adk_tool_without_prefix(tmp_path: Path):
    capability = LocalFilesCapability(allowed_roots=[tmp_path])
    tool = make_adk_tool(capability, "stat", prefix=False)

    assert tool.__name__ == "stat"


def test_make_adk_tool_unknown_operation_raises(tmp_path: Path):
    capability = LocalFilesCapability(allowed_roots=[tmp_path])

    with pytest.raises(CapabilityError, match="not found"):
        make_adk_tool(capability, "missing_operation")


def test_capability_to_adk_tools_count(tmp_path: Path):
    capability = LocalFilesCapability(allowed_roots=[tmp_path])
    tools = capability_to_adk_tools(capability)

    assert len(tools) == 10
    assert {tool.__name__ for tool in tools} == {
        "local_files_list_directory",
        "local_files_read_file",
        "local_files_write_file",
        "local_files_create_directory",
        "local_files_delete",
        "local_files_copy",
        "local_files_move",
        "local_files_search",
        "local_files_grep",
        "local_files_stat",
    }


def test_capability_to_adk_tools_subset(tmp_path: Path):
    capability = LocalFilesCapability(allowed_roots=[tmp_path])
    tools = capability_to_adk_tools(
        capability,
        operations=["list_directory", "read_file"],
    )

    assert len(tools) == 2
    assert tools[0].__name__ == "local_files_list_directory"
    assert tools[1].__name__ == "local_files_read_file"


def test_adk_tool_delegates_to_capability(tmp_path: Path):
    capability = LocalFilesCapability(allowed_roots=[tmp_path])
    tool = make_adk_tool(capability, "write_file")

    result = tool(str(tmp_path / "demo.txt"), "hello")
    assert result == {"success": True}

    read_tool = make_adk_tool(capability, "read_file")
    assert read_tool(str(tmp_path / "demo.txt"))["content"] == "hello"


def test_registry_to_adk_tools(tmp_path: Path):
    registry = CapabilityRegistry()
    registry.register(LocalFilesCapability(allowed_roots=[tmp_path]))

    tools = registry_to_adk_tools(registry)

    assert len(tools) == 10


def test_describe_capabilities_includes_operations(tmp_path: Path):
    registry = CapabilityRegistry()
    registry.register(LocalFilesCapability(allowed_roots=[tmp_path]))

    summary = describe_capabilities(registry)

    assert "local_files" in summary
    assert "list_directory" in summary
    assert "read_file" in summary
