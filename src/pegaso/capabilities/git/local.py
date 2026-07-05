"""Local subprocess implementation of the git capability."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

from pegaso.capabilities.git.descriptor import GIT_DESCRIPTOR
from pegaso.core.descriptor import CapabilityDescriptor
from pegaso.core.errors import CapabilityError


class LocalGitCapability:
    """Git capability backed by the local git CLI."""

    def __init__(self, repo_path: str | Path | None = None) -> None:
        self._repo_path = Path(repo_path or Path.cwd()).resolve()

    @property
    def descriptor(self) -> CapabilityDescriptor:
        return GIT_DESCRIPTOR

    @property
    def repo_path(self) -> Path:
        return self._repo_path

    def status(self) -> dict[str, str]:
        result = self._run("status")
        return {"output": result.stdout}

    def diff(
        self,
        *,
        staged: bool = False,
        target: str | None = None,
        context_lines: int = 3,
    ) -> dict[str, str]:
        args = [f"--unified={context_lines}"]
        if staged:
            args.append("--cached")
        elif target is not None:
            args.append(target)
        result = self._run("diff", *args)
        return {"output": result.stdout}

    def add(self, files: list[str]) -> dict[str, Any]:
        if not files:
            raise CapabilityError("At least one file path is required for add")
        result = self._run("add", "--", *files)
        return {"success": True, "output": result.stdout}

    def commit(self, message: str) -> dict[str, Any]:
        if not message.strip():
            raise CapabilityError("Commit message cannot be empty")
        result = self._run("commit", "-m", message)
        commit_hash = _extract_commit_hash(result.stdout)
        return {
            "success": True,
            "commit_hash": commit_hash,
            "output": result.stdout,
        }

    def checkout(self, branch: str) -> dict[str, Any]:
        result = self._run("checkout", branch)
        return {"success": True, "output": result.stdout}

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
            args = ["branch", name]
            if base_branch:
                args.append(base_branch)
            result = self._run(*args)
            return {"success": True, "output": result.stdout}

        flag = _branch_type_flag(branch_type)
        args = ["branch"]
        if flag:
            args.append(flag)
        result = self._run(*args)
        branches = _parse_branch_list(result.stdout)
        return {"branches": branches, "output": result.stdout}

    def log(
        self,
        max_count: int = 10,
        *,
        start_timestamp: str | None = None,
        end_timestamp: str | None = None,
    ) -> dict[str, Any]:
        args = [f"-{max_count}", "--format=%H|%an|%ae|%aI|%s"]
        if start_timestamp:
            args.extend(["--since", start_timestamp])
        if end_timestamp:
            args.extend(["--until", end_timestamp])
        result = self._run("log", *args)
        commits = _parse_log_entries(result.stdout)
        return {"commits": commits, "output": result.stdout}

    def show(self, revision: str = "HEAD") -> dict[str, str]:
        result = self._run("show", revision)
        return {"output": result.stdout}

    def pull(
        self,
        remote: str = "origin",
        branch: str | None = None,
    ) -> dict[str, Any]:
        args = ["pull", remote]
        if branch:
            args.append(branch)
        result = self._run(*args)
        return {"success": True, "output": result.stdout}

    def push(
        self,
        remote: str = "origin",
        branch: str | None = None,
    ) -> dict[str, Any]:
        args = ["push", remote]
        if branch:
            args.append(branch)
        result = self._run(*args)
        return {"success": True, "output": result.stdout}

    def clone(self, url: str, destination: str) -> dict[str, Any]:
        destination_path = Path(destination).resolve()
        result = _run_git(None, "clone", url, str(destination_path))
        return {"success": True, "output": result.stdout}

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return _run_git(self._repo_path, *args)


def _run_git(
    repo_path: Path | None,
    *args: str,
) -> subprocess.CompletedProcess[str]:
    command = ["git"]
    if repo_path is not None:
        command.extend(["-C", str(repo_path)])
    command.extend(args)

    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        message = (exc.stderr or exc.stdout or str(exc)).strip()
        raise CapabilityError(message or "Git command failed") from exc
    except FileNotFoundError as exc:
        raise CapabilityError(
            "Git executable not found. Install Git and ensure it is on PATH."
        ) from exc


def _branch_type_flag(branch_type: str) -> str:
    match branch_type:
        case "local":
            return ""
        case "remote":
            return "-r"
        case "all":
            return "-a"
        case _:
            raise CapabilityError(
                f"Invalid branch_type: {branch_type}. Use local, remote, or all."
            )


def _parse_branch_list(output: str) -> list[str]:
    branches: list[str] = []
    for line in output.splitlines():
        cleaned = line.strip().lstrip("* ").strip()
        if cleaned:
            branches.append(cleaned)
    return branches


def _parse_log_entries(output: str) -> list[dict[str, str]]:
    commits: list[dict[str, str]] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("|", 4)
        if len(parts) != 5:
            continue
        commits.append(
            {
                "hash": parts[0],
                "author": parts[1],
                "email": parts[2],
                "date": parts[3],
                "message": parts[4],
            }
        )
    return commits


def _extract_commit_hash(output: str) -> str | None:
    match = re.search(r"\b[0-9a-f]{7,40}\b", output)
    return match.group(0) if match else None
