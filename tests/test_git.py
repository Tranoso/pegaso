"""Tests for git capability operations."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from pegaso.capabilities.git import LocalGitCapability, configure, create_git_capability
from pegaso.capabilities.git.descriptor import GIT_DESCRIPTOR
from pegaso.core.errors import CapabilityError


@pytest.fixture
def git_repo(tmp_path: Path) -> LocalGitCapability:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(
        ["git", "init", str(repo)],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@example.com"],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "Test User"],
        check=True,
        capture_output=True,
        text=True,
    )
    return LocalGitCapability(repo)


def test_descriptor_lists_required_operations():
    operation_names = {operation.name for operation in GIT_DESCRIPTOR.operations}
    assert operation_names == {
        "status",
        "diff",
        "add",
        "commit",
        "checkout",
        "branch",
        "log",
        "show",
        "pull",
        "push",
        "clone",
    }


def test_status_on_clean_repo(git_repo: LocalGitCapability):
    result = git_repo.status()
    assert "output" in result
    assert isinstance(result["output"], str)


def test_add_commit_and_log(git_repo: LocalGitCapability, tmp_path: Path):
    file_path = git_repo.repo_path / "hello.txt"
    file_path.write_text("hello")

    add_result = git_repo.add(["hello.txt"])
    assert add_result["success"] is True

    commit_result = git_repo.commit("Initial implementation")
    assert commit_result["success"] is True
    assert commit_result["commit_hash"]

    log_result = git_repo.log(max_count=5)
    assert len(log_result["commits"]) == 1
    assert log_result["commits"][0]["message"] == "Initial implementation"


def test_diff_and_show(git_repo: LocalGitCapability):
    file_path = git_repo.repo_path / "tracked.txt"
    file_path.write_text("v1")
    git_repo.add(["tracked.txt"])
    git_repo.commit("Add tracked file")

    file_path.write_text("v2")
    diff_result = git_repo.diff()
    assert "v1" in diff_result["output"] or "v2" in diff_result["output"]

    git_repo.add(["tracked.txt"])
    staged_diff = git_repo.diff(staged=True)
    assert staged_diff["output"]

    show_result = git_repo.show("HEAD")
    assert "Add tracked file" in show_result["output"]


def test_branch_and_checkout(git_repo: LocalGitCapability):
    (git_repo.repo_path / "base.txt").write_text("base")
    git_repo.add(["base.txt"])
    git_repo.commit("Base commit")

    create_result = git_repo.branch("feature", create=True)
    assert create_result["success"] is True

    checkout_result = git_repo.checkout("feature")
    assert checkout_result["success"] is True

    branches = git_repo.branch(branch_type="local")
    assert "feature" in branches["branches"]


def test_clone(git_repo: LocalGitCapability, tmp_path: Path):
    source = git_repo.repo_path
    (source / "clone-me.txt").write_text("clone")
    git_repo.add(["clone-me.txt"])
    git_repo.commit("Prepare clone")

    destination = tmp_path / "cloned"
    clone_result = git_repo.clone(str(source), str(destination))
    assert clone_result["success"] is True
    assert (destination / "clone-me.txt").read_text() == "clone"


def test_commit_requires_message(git_repo: LocalGitCapability):
    with pytest.raises(CapabilityError, match="Commit message cannot be empty"):
        git_repo.commit("   ")


def test_create_git_capability_falls_back_without_mcp(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(
        "pegaso.capabilities.git.factory._mcp_available",
        lambda: False,
    )
    capability = create_git_capability(tmp_path, prefer_mcp=True)
    assert isinstance(capability, LocalGitCapability)


def test_module_level_api(git_repo: LocalGitCapability):
    configure(git_repo.repo_path, prefer_mcp=False)

    (git_repo.repo_path / "module.txt").write_text("module")
    from pegaso.capabilities import git as git_module

    git_module.add(["module.txt"])
    result = git_module.commit("Module commit")
    assert result["success"] is True

    status = git_module.status()
    assert "output" in status
