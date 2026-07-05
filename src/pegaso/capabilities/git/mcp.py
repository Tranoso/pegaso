"""MCP-backed implementation of the git capability."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

from pegaso.capabilities.git.descriptor import GIT_DESCRIPTOR
from pegaso.capabilities.git.local import LocalGitCapability
from pegaso.core.descriptor import CapabilityDescriptor
from pegaso.core.errors import CapabilityError
from pegaso.core.mcp_client import McpServerConfig, call_mcp_tool

class McpGitCapability:
    """Git capability that delegates to mcp-server-git when possible."""

    def __init__(
        self,
        repo_path: str | Path | None = None,
        *,
        server_command: str | None = None,
        server_args: tuple[str, ...] | None = None,
    ) -> None:
        self._repo_path = Path(repo_path or Path.cwd()).resolve()
        self._local = LocalGitCapability(self._repo_path)
        if server_args is None:
            server_args = (
                "-m",
                "mcp_server_git",
                "--repository",
                str(self._repo_path),
            )
        self._server = McpServerConfig(
            command=server_command or sys.executable,
            args=server_args,
        )

    @property
    def descriptor(self) -> CapabilityDescriptor:
        descriptor = GIT_DESCRIPTOR
        return CapabilityDescriptor(
            name=descriptor.name,
            domain=descriptor.domain,
            description=descriptor.description,
            deterministic=descriptor.deterministic,
            side_effects=descriptor.side_effects,
            typical_latency=descriptor.typical_latency,
            network_required=True,
            operations=descriptor.operations,
            metadata={
                **descriptor.metadata,
                "backend": "mcp-server-git",
            },
        )

    @property
    def repo_path(self) -> Path:
        return self._repo_path

    def status(self) -> dict[str, str]:
        output = self._call_mcp("git_status", {})
        return {"output": _strip_prefix(output, "Repository status:")}

    def diff(
        self,
        *,
        staged: bool = False,
        target: str | None = None,
        context_lines: int = 3,
    ) -> dict[str, str]:
        arguments = {
            "repo_path": str(self._repo_path),
            "context_lines": context_lines,
        }
        if target is not None:
            arguments["target"] = target
            tool_name = "git_diff"
            prefix = f"Diff with {target}:"
        elif staged:
            tool_name = "git_diff_staged"
            prefix = "Staged changes:"
        else:
            tool_name = "git_diff_unstaged"
            prefix = "Unstaged changes:"

        output = self._call_mcp(tool_name, arguments)
        return {"output": _strip_prefix(output, prefix)}

    def add(self, files: list[str]) -> dict[str, Any]:
        if not files:
            raise CapabilityError("At least one file path is required for add")
        output = self._call_mcp("git_add", {"files": files})
        return {"success": True, "output": output}

    def commit(self, message: str) -> dict[str, Any]:
        if not message.strip():
            raise CapabilityError("Commit message cannot be empty")
        output = self._call_mcp("git_commit", {"message": message})
        commit_hash = _extract_commit_hash(output)
        return {
            "success": True,
            "commit_hash": commit_hash,
            "output": output,
        }

    def checkout(self, branch: str) -> dict[str, Any]:
        output = self._call_mcp("git_checkout", {"branch_name": branch})
        return {"success": True, "output": output}

    def branch(
        self,
        name: str | None = None,
        *,
        create: bool = False,
        base_branch: str | None = None,
        branch_type: str = "local",
    ) -> dict[str, Any]:
        if create:
            if not name:
                raise CapabilityError("Branch name is required when create=True")
            arguments: dict[str, Any] = {"branch_name": name}
            if base_branch:
                arguments["base_branch"] = base_branch
            output = self._call_mcp("git_create_branch", arguments)
            return {"success": True, "output": output}

        output = self._call_mcp(
            "git_branch",
            {
                "branch_type": branch_type,
            },
        )
        branches = [line.strip() for line in output.splitlines() if line.strip()]
        return {"branches": branches, "output": output}

    def log(
        self,
        max_count: int = 10,
        *,
        start_timestamp: str | None = None,
        end_timestamp: str | None = None,
    ) -> dict[str, Any]:
        arguments: dict[str, Any] = {"max_count": max_count}
        if start_timestamp:
            arguments["start_timestamp"] = start_timestamp
        if end_timestamp:
            arguments["end_timestamp"] = end_timestamp
        output = self._call_mcp("git_log", arguments)
        cleaned = _strip_prefix(output, "Commit history:")
        commits = _parse_mcp_log(cleaned)
        return {"commits": commits, "output": cleaned}

    def show(self, revision: str = "HEAD") -> dict[str, str]:
        output = self._call_mcp("git_show", {"revision": revision})
        return {"output": output}

    def pull(
        self,
        remote: str = "origin",
        branch: str | None = None,
    ) -> dict[str, Any]:
        return self._local.pull(remote=remote, branch=branch)

    def push(
        self,
        remote: str = "origin",
        branch: str | None = None,
    ) -> dict[str, Any]:
        return self._local.push(remote=remote, branch=branch)

    def clone(self, url: str, destination: str) -> dict[str, Any]:
        return self._local.clone(url=url, destination=destination)

    def _call_mcp(self, tool_name: str, arguments: dict[str, Any]) -> str:
        payload = {"repo_path": str(self._repo_path), **arguments}
        try:
            return call_mcp_tool(self._server, tool_name, payload)
        except ImportError:
            raise
        except Exception as exc:
            raise CapabilityError(
                f"MCP git tool '{tool_name}' failed: {exc}"
            ) from exc


def _strip_prefix(output: str, prefix: str) -> str:
    cleaned = output.strip()
    if cleaned.startswith(prefix):
        return cleaned[len(prefix) :].strip()
    return cleaned


def _extract_commit_hash(output: str) -> str | None:
    match = re.search(r"\b[0-9a-f]{7,40}\b", output)
    return match.group(0) if match else None


def _parse_mcp_log(output: str) -> list[dict[str, str]]:
    commits: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in output.splitlines():
        if line.startswith("Commit: "):
            if current:
                commits.append(current)
            current = {"hash": line.removeprefix("Commit: ").strip()}
        elif line.startswith("Author: "):
            current["author"] = line.removeprefix("Author: ").strip()
        elif line.startswith("Date: "):
            current["date"] = line.removeprefix("Date: ").strip()
        elif line.startswith("Message: "):
            current["message"] = line.removeprefix("Message: ").strip()
    if current:
        commits.append(current)
    return commits
