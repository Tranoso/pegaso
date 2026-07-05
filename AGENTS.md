# AGENTS.md

## Project overview

PEGASO is a capability library for intelligent systems. Capabilities expose a consistent, self-describing interface regardless of implementation.

## Setup

```bash
pip install -e ".[dev]"
```

## Run tests

```bash
pytest
```

## Package layout

```
src/pegaso/
├── core/                  # Capability protocol, registry, descriptors
└── capabilities/
    └── local_files/       # Local filesystem capability
```

## Adding capabilities

1. Define a contract protocol in `capabilities/<name>/contract.py`
2. Add self-description in `capabilities/<name>/descriptor.py`
3. Implement the capability in `capabilities/<name>/local.py` (or other backend)
4. Register via `CapabilityRegistry` in consumer code
