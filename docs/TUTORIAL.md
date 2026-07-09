# PEGASO Tutorial: Using Capabilities with Google ADK

This tutorial walks through PEGASO from first principles to a working
[Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) agent.

PEGASO provides **capabilities** — reusable, self-describing building blocks
such as filesystem access, Git, and BigQuery. ADK provides the **agent runtime**
— orchestration, LLM calls, and tool execution. Together they let you give an
agent real-world abilities without re-implementing tools for every project.

---

## Table of contents

1. [Install PEGASO](#1-install-pegaso)
2. [Core concepts](#2-core-concepts)
3. [Your first capability](#3-your-first-capability)
4. [The capability registry](#4-the-capability-registry)
5. [Google ADK in brief](#5-google-adk-in-brief)
6. [Bridging PEGASO to ADK](#6-bridging-pegaso-to-adk)
7. [Build a file assistant agent](#7-build-a-file-assistant-agent)
8. [Run the agent](#8-run-the-agent)
9. [Add more capabilities](#9-add-more-capabilities)
10. [Design notes](#10-design-notes)

---

## 1. Install PEGASO

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

For the ADK example later, also install the ADK extra:

```bash
pip install -e ".[adk]"
```

---

## 2. Core concepts

PEGASO is built around four ideas:

| Concept | What it is | Where it lives |
|---------|-----------|----------------|
| **Contract** | A protocol defining what operations a capability exposes | `capabilities/<name>/contract.py` |
| **Descriptor** | Self-description metadata (name, inputs, outputs) | `capabilities/<name>/descriptor.py` |
| **Implementation** | The actual code that performs work | `capabilities/<name>/local.py`, `mcp.py`, etc. |
| **Registry** | A lookup table for capabilities by name | `pegaso.core.registry` |

Every capability implements the base `Capability` protocol, which only
requires a `descriptor` property:

```python
from pegaso import Capability, CapabilityDescriptor

# Every capability exposes self-description:
descriptor = capability.descriptor
print(descriptor.name)          # e.g. "local_files"
print(descriptor.operations)    # list of OperationDescriptor
```

Consumers depend on **contracts**, not implementations. Whether filesystem
access runs as local Python code or through an MCP server should not matter
to the agent.

---

## 3. Your first capability

The `local_files` capability is the simplest place to start. It provides
sandboxed filesystem access inside one or more allowed root directories.

```python
from pathlib import Path
from pegaso.capabilities.local_files import LocalFilesCapability

workspace = Path("./workspace")
workspace.mkdir(exist_ok=True)

files = LocalFilesCapability(allowed_roots=[workspace])

# List contents
print(files.list_directory("."))

# Write and read
files.write_file("notes.txt", "Hello from PEGASO")
print(files.read_file("notes.txt"))
```

Every operation returns a **plain dict** — JSON-friendly and easy for an LLM
to consume:

```python
>>> files.read_file("notes.txt")
{'content': 'Hello from PEGASO', 'encoding': 'utf-8', 'size': 17}
```

The capability also describes itself:

```python
descriptor = files.descriptor
print(descriptor.name)        # local_files
print(descriptor.domain)      # Filesystem
print(len(descriptor.operations))  # 10
```

Available operations include `list_directory`, `read_file`, `write_file`,
`create_directory`, `delete`, `copy`, `move`, `search`, `grep`, and `stat`.

Paths outside the allowed roots are rejected by the built-in `PathGuard`.

---

## 4. The capability registry

When an agent needs multiple capabilities, register them in a
`CapabilityRegistry`:

```python
from pegaso.capabilities.local_files import LocalFilesCapability
from pegaso.core.registry import CapabilityRegistry

registry = CapabilityRegistry()
registry.register(LocalFilesCapability(allowed_roots=["./workspace"]))

# Resolve by name
files = registry.get("local_files")
print(registry.list_names())  # ['local_files']
```

The registry is intentionally minimal. It does not orchestrate agents or
manage sessions — that is ADK's job.

---

## 5. Google ADK in brief

[Google ADK](https://google.github.io/adk-docs/) is an open-source framework
for building AI agents. You define an agent with a model, instructions, and a
list of **tools**. ADK handles the conversation loop and tool-calling protocol.

A minimal ADK agent looks like this:

```python
from google.adk.agents import Agent

def greet(name: str) -> dict:
    """Say hello to someone.

    Args:
        name: The person's name.
    """
    return {"message": f"Hello, {name}!"}

root_agent = Agent(
    name="greeter",
    model="gemini-2.0-flash",
    instruction="You are a friendly greeter.",
    tools=[greet],  # plain functions become FunctionTools automatically
)
```

ADK inspects each function's **name**, **docstring**, **type hints**, and
**default values** to build the tool schema the LLM sees. Well-documented
functions produce better tool use.

---

## 6. Bridging PEGASO to ADK

PEGASO capabilities are Python objects with methods, not standalone
functions. The `pegaso.integrations.google_adk` module converts them into
ADK-compatible function tools using each capability's self-description.

```python
from pegaso.capabilities.local_files import LocalFilesCapability
from pegaso.core.registry import CapabilityRegistry
from pegaso.integrations.google_adk import (
    capability_to_adk_tools,
    describe_capabilities,
    registry_to_adk_tools,
)

files = LocalFilesCapability(allowed_roots=["./workspace"])

# Option A: convert a single capability
tools = capability_to_adk_tools(files)

# Option B: convert everything in a registry
registry = CapabilityRegistry()
registry.register(files)
tools = registry_to_adk_tools(registry)

# Each tool is a plain function ADK can use directly
print(tools[0].__name__)   # local_files_list_directory
print(tools[0].__doc__)    # generated from the capability descriptor
```

### What the bridge does

For each operation in a capability's descriptor, the bridge:

1. Wraps the underlying method in a standalone function.
2. Copies the method's type signature so ADK knows required vs optional args.
3. Builds a docstring from the `OperationDescriptor` inputs and outputs.
4. Names the tool `{capability}_{operation}` (e.g. `local_files_read_file`).

Use `describe_capabilities(registry)` to generate a tool summary you can
paste into the agent's system instruction:

```python
instruction = f"""You are a file assistant.

{describe_capabilities(registry)}

Always verify a path exists before modifying files.
"""
```

### Select specific operations

To expose only a subset of operations (for example, read-only tools):

```python
read_only = capability_to_adk_tools(
    files,
    operations=["list_directory", "read_file", "search", "grep", "stat"],
)
```

---

## 7. Build a file assistant agent

The repository includes a complete example at
`examples/adk_file_assistant/`. Here is how it is structured.

### Project layout

```
examples/
└── adk_file_assistant/
    ├── __init__.py
    ├── agent.py          # defines root_agent
    ├── .env.example      # API key template
    └── README.md
```

ADK expects a folder with an `agent.py` that exports `root_agent`.

### agent.py

```python
import os
from pathlib import Path

from google.adk.agents import Agent

from pegaso.capabilities.local_files import LocalFilesCapability
from pegaso.core.registry import CapabilityRegistry
from pegaso.integrations.google_adk import (
    describe_capabilities,
    registry_to_adk_tools,
)

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

You work inside a sandboxed directory. Use relative paths.

{describe_capabilities(registry)}

Prefer read-only operations when answering questions.
Confirm before deleting files.
""",
    tools=tools,
)
```

### Environment variables

Copy `.env.example` to `.env` and set your Gemini API key:

```bash
cp examples/adk_file_assistant/.env.example examples/adk_file_assistant/.env
```

```
GOOGLE_API_KEY=your-api-key-here
PEGASO_WORKSPACE=./workspace
```

Get a key from [Google AI Studio](https://aistudio.google.com/apikey).

---

## 8. Run the agent

From the repository root, with ADK installed:

```bash
# Interactive web UI (recommended for development)
adk web examples/

# Or run in the terminal
adk run examples/adk_file_assistant
```

In the web UI, select **file_assistant** and try prompts like:

- "List the files in the workspace."
- "Create a file called todo.md with three items."
- "Search for the word PEGASO in all text files."

The agent calls PEGASO tools (`local_files_list_directory`,
`local_files_write_file`, etc.) and ADK handles the LLM conversation.

---

## 9. Add more capabilities

PEGASO ships additional capabilities you can register the same way.

### Git

```python
from pegaso.capabilities.git import create_git_capability

registry.register(create_git_capability("/path/to/repo"))
tools = registry_to_adk_tools(registry)
```

Git supports local and MCP backends. Install MCP support with
`pip install -e ".[git-mcp]"`.

### BigQuery

```python
from pegaso.capabilities.bigquery import create_bigquery_capability

registry.register(
    create_bigquery_capability(project_id="my-project")
)
```

Install with `pip install -e ".[bigquery]"` or `".[bigquery-mcp]"`.

### Mixing capabilities

```python
registry = CapabilityRegistry()
registry.register(LocalFilesCapability(allowed_roots=["./workspace"]))
registry.register(create_git_capability("."))
registry.register(create_bigquery_capability(project_id="my-project"))

all_tools = registry_to_adk_tools(registry)
```

Each capability's operations become individually named ADK tools. Update the
agent instruction with `describe_capabilities(registry)` so the LLM knows
what is available.

---

## 10. Design notes

### PEGASO is not an agent framework

PEGASO deliberately stops at capabilities. It does not manage conversation
history, plan multi-step workflows, or choose which tool to call. ADK (or
LangGraph, CrewAI, or your own loop) owns orchestration.

This separation means:

- Capabilities are reusable across agent frameworks.
- You can swap ADK for another runtime without rewriting capabilities.
- Business logic stays in your agent, not in PEGASO.

### Self-description drives tool schemas

PEGASO descriptors are the single source of truth for tool metadata. When you
add a new operation to a capability, update its `descriptor.py` and the ADK
bridge picks it up automatically.

### Sandboxing matters

Always constrain filesystem capabilities with explicit `allowed_roots`. The
example agent uses `PEGASO_WORKSPACE` so the LLM cannot escape the intended
directory.

### When to write custom ADK tools instead

Use the PEGASO bridge when a capability already exists or you want
implementation-agnostic contracts. Write plain ADK function tools when the
logic is agent-specific and will not be reused — for example, formatting a
report for a single use case.

---

## Next steps

- Browse `tests/` for more capability usage examples.
- Read `AGENTS.md` for instructions on adding new capabilities.
- Explore the [ADK documentation](https://google.github.io/adk-docs/) for
  multi-agent patterns, MCP tool integration, and deployment options.
