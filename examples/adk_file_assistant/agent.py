"""File assistant agent powered by PEGASO local_files and Google ADK."""

from __future__ import annotations

import os
from pathlib import Path

from google.adk.agents import Agent

from pegaso.capabilities.local_files import LocalFilesCapability
from pegaso.core.registry import CapabilityRegistry
from pegaso.integrations.google_adk import describe_capabilities, registry_to_adk_tools

workspace = Path(os.environ.get("PEGASO_WORKSPACE", "./workspace"))
workspace.mkdir(parents=True, exist_ok=True)

registry = CapabilityRegistry()
registry.register(LocalFilesCapability(allowed_roots=[workspace]))

tools = registry_to_adk_tools(registry)

root_agent = Agent(
    name="file_assistant",
    model="gemini-2.0-flash",
    description="Explores and edits files in a sandboxed workspace.",
    instruction=f"""You are a helpful file assistant.

You work inside a sandboxed directory. Use relative paths from the workspace root.

{describe_capabilities(registry)}

Prefer read-only operations when answering questions.
Confirm before deleting files.
""",
    tools=tools,
)
