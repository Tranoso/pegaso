"""Bridge PEGASO capabilities to Google ADK function tools."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any

from pegaso.core.capability import Capability
from pegaso.core.descriptor import CapabilityDescriptor, OperationDescriptor
from pegaso.core.errors import CapabilityError
from pegaso.core.registry import CapabilityRegistry


def _find_operation(
    descriptor: CapabilityDescriptor,
    operation_name: str,
) -> OperationDescriptor:
    for operation in descriptor.operations:
        if operation.name == operation_name:
            return operation
    raise CapabilityError(
        f"Operation '{operation_name}' not found on capability '{descriptor.name}'"
    )


def _operation_docstring(
    operation: OperationDescriptor,
    signature: inspect.Signature,
) -> str:
    lines = [operation.description, ""]
    parameters = [
        (name, param)
        for name, param in signature.parameters.items()
        if name != "self"
    ]
    if parameters:
        lines.append("Args:")
        for name, param in parameters:
            description = operation.inputs.get(name, "")
            if param.default is not inspect.Parameter.empty:
                lines.append(
                    f"    {name} (optional): {description}".rstrip()
                )
            else:
                lines.append(f"    {name}: {description}".rstrip())
    if operation.outputs:
        lines.append("")
        lines.append("Returns:")
        lines.append("    dict with keys:")
        for key, description in operation.outputs.items():
            lines.append(f"        {key}: {description}")
    return "\n".join(lines)


def make_adk_tool(
    capability: Capability,
    operation_name: str,
    *,
    prefix: bool = True,
) -> Callable[..., dict[str, Any]]:
    """Wrap a single capability operation as an ADK-compatible function tool.

    ADK inspects the returned function's name, docstring, and signature to
    build the tool schema for the LLM. The function delegates to the
    underlying capability method unchanged.
    """

    descriptor = capability.descriptor
    operation = _find_operation(descriptor, operation_name)
    method = getattr(capability, operation_name, None)
    if method is None or not callable(method):
        raise CapabilityError(
            f"Capability '{descriptor.name}' has no callable '{operation_name}'"
        )

    signature = inspect.signature(method)
    tool_name = f"{descriptor.name}_{operation_name}" if prefix else operation_name

    def tool_impl(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return method(*args, **kwargs)

    tool_impl.__name__ = tool_name
    tool_impl.__qualname__ = tool_name
    tool_impl.__doc__ = _operation_docstring(operation, signature)
    tool_impl.__signature__ = signature
    tool_impl.__annotations__ = dict(getattr(method, "__annotations__", {}))
    return tool_impl


def capability_to_adk_tools(
    capability: Capability,
    *,
    prefix: bool = True,
    operations: list[str] | None = None,
) -> list[Callable[..., dict[str, Any]]]:
    """Convert every operation on a capability into ADK function tools."""

    descriptor = capability.descriptor
    selected = operations or [op.name for op in descriptor.operations]
    return [
        make_adk_tool(capability, name, prefix=prefix)
        for name in selected
    ]


def registry_to_adk_tools(
    registry: CapabilityRegistry,
    *,
    names: list[str] | None = None,
    prefix: bool = True,
) -> list[Callable[..., dict[str, Any]]]:
    """Convert registered capabilities into a flat list of ADK function tools."""

    tools: list[Callable[..., dict[str, Any]]] = []
    for name in names or registry.list_names():
        capability = registry.get(name)
        tools.extend(capability_to_adk_tools(capability, prefix=prefix))
    return tools


def describe_capabilities(registry: CapabilityRegistry) -> str:
    """Build a human-readable tool summary for agent instructions."""

    sections: list[str] = []
    for name in registry.list_names():
        capability = registry.get(name)
        descriptor = capability.descriptor
        lines = [
            f"## {descriptor.name} ({descriptor.domain})",
            descriptor.description,
            "",
            "Operations:",
        ]
        for operation in descriptor.operations:
            input_summary = ", ".join(operation.inputs) or "none"
            lines.append(
                f"- **{operation.name}**: {operation.description} "
                f"(inputs: {input_summary})"
            )
        sections.append("\n".join(lines))
    return "\n\n".join(sections)
