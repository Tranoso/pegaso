"""Tests for local_files capability operations."""

from pathlib import Path

import pytest

from pegaso.capabilities.local_files import LocalFilesCapability
from pegaso.core.errors import CapabilityError, PathAccessError


def test_list_directory(sandbox, tmp_path: Path):
    (tmp_path / "alpha.txt").write_text("a")
    (tmp_path / "subdir").mkdir()

    result = sandbox.list_directory(str(tmp_path))

    assert result["directories"] == ["subdir"]
    assert result["files"] == ["alpha.txt"]


def test_read_and_write_file(sandbox, tmp_path: Path):
    file_path = tmp_path / "hello.txt"

    write_result = sandbox.write_file(str(file_path), "hello world")
    assert write_result["success"] is True

    read_result = sandbox.read_file(str(file_path))
    assert read_result["content"] == "hello world"
    assert read_result["encoding"] == "utf-8"
    assert read_result["size"] == 11


def test_write_file_no_overwrite(sandbox, tmp_path: Path):
    file_path = tmp_path / "existing.txt"
    file_path.write_text("original")

    with pytest.raises(CapabilityError, match="already exists"):
        sandbox.write_file(str(file_path), "new", overwrite=False)


def test_create_directory(sandbox, tmp_path: Path):
    nested = tmp_path / "a" / "b" / "c"
    result = sandbox.create_directory(str(nested))

    assert result["success"] is True
    assert nested.is_dir()


def test_delete_file_and_directory(sandbox, tmp_path: Path):
    file_path = tmp_path / "remove.txt"
    file_path.write_text("bye")
    dir_path = tmp_path / "remove_dir"
    dir_path.mkdir()
    (dir_path / "inner.txt").write_text("inner")

    assert sandbox.delete(str(file_path))["success"] is True
    assert not file_path.exists()

    assert sandbox.delete(str(dir_path))["success"] is True
    assert not dir_path.exists()


def test_copy_and_move(sandbox, tmp_path: Path):
    source = tmp_path / "source.txt"
    source.write_text("payload")

    copy_dest = tmp_path / "copied.txt"
    assert sandbox.copy(str(source), str(copy_dest))["success"] is True
    assert copy_dest.read_text() == "payload"

    move_dest = tmp_path / "moved.txt"
    assert sandbox.move(str(copy_dest), str(move_dest))["success"] is True
    assert move_dest.read_text() == "payload"
    assert not copy_dest.exists()


def test_copy_directory(sandbox, tmp_path: Path):
    source_dir = tmp_path / "src_dir"
    source_dir.mkdir()
    (source_dir / "file.txt").write_text("data")

    dest_dir = tmp_path / "dst_dir"
    assert sandbox.copy(str(source_dir), str(dest_dir))["success"] is True
    assert (dest_dir / "file.txt").read_text() == "data"


def test_search(sandbox, tmp_path: Path):
    (tmp_path / "match.py").write_text("x")
    (tmp_path / "other.txt").write_text("x")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "also.py").write_text("x")

    result = sandbox.search(str(tmp_path), "*.py", recursive=True)
    paths = {Path(p).name for p in result["matching_paths"]}
    assert paths == {"also.py", "match.py"}


def test_search_non_recursive(sandbox, tmp_path: Path):
    (tmp_path / "top.py").write_text("x")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "deep.py").write_text("x")

    result = sandbox.search(str(tmp_path), "*.py", recursive=False)
    assert result["matching_paths"] == ["top.py"]


def test_grep(sandbox, tmp_path: Path):
    (tmp_path / "a.txt").write_text("hello\nworld\nhello again\n")
    (tmp_path / "b.txt").write_text("nothing here\n")

    result = sandbox.grep(str(tmp_path), "hello")
    assert result["matching_files"] == ["a.txt"]
    assert len(result["matching_lines"]) == 2
    assert result["matching_lines"][0]["line_number"] == 1
    assert result["matching_lines"][0]["line"] == "hello"


def test_stat_file(sandbox, tmp_path: Path):
    file_path = tmp_path / "stat.txt"
    file_path.write_text("stats")

    result = sandbox.stat(str(file_path))
    assert result["size"] == 5
    assert result["file_type"] == "file"
    assert "created_time" in result
    assert "modified_time" in result
    assert "permissions" in result


def test_stat_directory(sandbox, tmp_path: Path):
    result = sandbox.stat(str(tmp_path))
    assert result["file_type"] == "directory"


def test_path_guard_blocks_outside_root(tmp_path: Path):
    outside = tmp_path.parent / "outside"
    outside.mkdir(exist_ok=True)
    sandbox = LocalFilesCapability(allowed_roots=[tmp_path / "sandbox"])
    (tmp_path / "sandbox").mkdir(exist_ok=True)

    with pytest.raises(PathAccessError):
        sandbox.read_file(str(outside / "secret.txt"))


def test_path_traversal_blocked(tmp_path: Path):
    sandbox = LocalFilesCapability(allowed_roots=[tmp_path])
    secret = tmp_path.parent / "secret.txt"
    secret.write_text("secret")

    with pytest.raises(PathAccessError):
        sandbox.read_file(str(tmp_path / ".." / secret.name))


def test_relative_paths_resolve_from_root(sandbox, tmp_path: Path):
    sandbox.write_file("relative.txt", "relative content")
    result = sandbox.read_file("relative.txt")
    assert result["content"] == "relative content"
    assert (tmp_path / "relative.txt").exists()
