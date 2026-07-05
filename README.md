# PEGASO

> Build once. Use everywhere.

PEGASO is a capability library for intelligent systems.

Its purpose is simple:

Expose reusable capabilities through a consistent interface, regardless of their implementation.

---

# Philosophy

Software should depend on capabilities, not implementations.

Whether a capability is implemented as:

* local code
* an MCP server
* an HTTP service
* another process
* another AI

should not matter to its consumer.

Only the capability contract matters.

---

# What is a Capability?

A capability is something that can perform work.

Examples:

* Calculator
* Filesystem
* SQLite
* Git
* PostgreSQL
* HTTP Client
* Markdown
* CSV
* JSON

Capabilities may be local or remote.

From the consumer's perspective, they are all the same.

---

# Principles

## Uniform Interface

Every capability should expose a consistent interface.

Consumers should not care about implementation details.

---

## Replaceable Implementations

Implementations can change.

Interfaces should remain stable.

---

## Reusable by Design

Capabilities should be reusable across projects.

Business logic does not belong in PEGASO.

---

## Self Describing

Every capability should describe itself.

Examples:

* name
* description
* inputs
* outputs
* metadata

---

## Implementation Agnostic

PEGASO does not prefer any transport or execution model.

A capability may use:

* Python
* MCP
* HTTP
* IPC
* gRPC
* Future technologies

without changing its public contract.

---

# Goals

* Eliminate duplicated tools.
* Build reusable capabilities.
* Keep implementations replaceable.
* Encourage consistent interfaces.
* Make intelligent systems easier to compose.

---

# Non Goals

PEGASO is not:

* an agent framework
* a workflow engine
* an orchestration system
* a prompt library
* a business framework

It only provides capabilities.

---

# Design Rule

If a component can be reused without knowing the application domain, it probably belongs in PEGASO.

Otherwise, it belongs somewhere else.

---

# Vision

Capabilities should be portable.

Consumers should depend on contracts.

Implementations should be free to evolve.
