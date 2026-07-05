"""Local Python implementation of the local_files capability."""

from __future__ import annotations

import fnmatch
import shutil
import stat as stat_module
from datetime import datetime, timezone
from pathlib import Path

from pegaso.capabilities.local_files.descriptor import LOCAL_FILES_DESCRIPTOR
from pegaso.capabilities.local_files.security import PathGuard
from pegaso.core.descriptor import CapabilityDescriptor
from pegaso.core.errors import CapabilityError


class LocalFilesCapability:
    """Platform-independent local filesystem capability."""

    def __init__(self, allowed_roots: list[str | Path]) -> None:
        self._guard = PathGuard(allowed_roots)

    @property
    def descriptor(self) -> CapabilityDescriptor:
        return LOCAL_FILES_DESCRIPTOR

    def list_directory(self, path: str) -> dict[str, list[str]]:
        target = self._guard.resolve(path)
        if not target.is_dir():
            raise CapabilityError(f"Not a directory: {path}")

        directories: list[str] = []
        files: list[str] = []
        for entry in sorted(target.iterdir(), key=lambda item: item.name):
            if entry.is_dir():
                directories.append(entry.name)
            else:
                files.append(entry.name)

        return {"directories": directories, "files": files}

    def read_file(self, path: str) -> dict[str, object]:
        target = self._guard.resolve(path)
        if not target.is_file():
            raise CapabilityError(f"Not a file: {path}")

        raw = target.read_bytes()
        encoding = "utf-8"
        try:
            content = raw.decode(encoding)
        except UnicodeDecodeError:
            encoding = "base64"
            import base64

            content = base64.b64encode(raw).decode("ascii")

        return {
            "content": content,
            "encoding": encoding,
            "size": len(raw),
        }

    def write_file(
        self,
        path: str,
        content: str,
        overwrite: bool = True,
    ) -> dict[str, bool]:
        target = self._guard.resolve(path)
        if target.exists() and not overwrite:
            raise CapabilityError(f"File already exists: {path}")

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"success": True}

    def create_directory(self, path: str) -> dict[str, bool]:
        target = self._guard.resolve(path)
        target.mkdir(parents=True, exist_ok=True)
        return {"success": True}

    def delete(self, path: str) -> dict[str, bool]:
        target = self._guard.resolve(path)
        if not target.exists():
            raise CapabilityError(f"Path does not exist: {path}")

        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()

        return {"success": True}

    def copy(self, source: str, destination: str) -> dict[str, bool]:
        src = self._guard.resolve(source)
        dst = self._guard.resolve(destination)

        if not src.exists():
            raise CapabilityError(f"Source does not exist: {source}")

        if src.is_dir():
            if dst.exists():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copytree(src, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

        return {"success": True}

    def move(self, source: str, destination: str) -> dict[str, bool]:
        src = self._guard.resolve(source)
        dst = self._guard.resolve(destination)

        if not src.exists():
            raise CapabilityError(f"Source does not exist: {source}")

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return {"success": True}

    def search(
        self,
        root: str,
        pattern: str,
        recursive: bool = True,
    ) -> dict[str, list[str]]:
        base = self._guard.resolve(root)
        if not base.is_dir():
            raise CapabilityError(f"Not a directory: {root}")

        matching: list[str] = []
        iterator = base.rglob("*") if recursive else base.iterdir()

        for entry in iterator:
            if entry.is_file() and fnmatch.fnmatch(entry.name, pattern):
                matching.append(str(entry.relative_to(self._guard.roots[0])))

        return {"matching_paths": sorted(matching)}

    def grep(
        self,
        root: str,
        query: str,
        recursive: bool = True,
    ) -> dict[str, list[object]]:
        base = self._guard.resolve(root)
        if not base.is_dir():
            raise CapabilityError(f"Not a directory: {root}")

        matching_files: list[str] = []
        matching_lines: list[dict[str, object]] = []
        iterator = base.rglob("*") if recursive else base.iterdir()

        for entry in sorted(iterator, key=lambda item: str(item)):
            if not entry.is_file():
                continue

            try:
                text = entry.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue

            file_matches: list[dict[str, object]] = []
            for line_number, line in enumerate(text.splitlines(), start=1):
                if query in line:
                    file_matches.append(
                        {
                            "path": str(entry.relative_to(self._guard.roots[0])),
                            "line_number": line_number,
                            "line": line,
                        }
                    )

            if file_matches:
                matching_files.append(
                    str(entry.relative_to(self._guard.roots[0]))
                )
                matching_lines.extend(file_matches)

        return {
            "matching_files": matching_files,
            "matching_lines": matching_lines,
        }

    def stat(self, path: str) -> dict[str, object]:
        target = self._guard.resolve(path)
        if not target.exists():
            raise CapabilityError(f"Path does not exist: {path}")

        info = target.stat()
        file_type = "directory" if target.is_dir() else "file"
        if not target.is_dir() and not target.is_file():
            file_type = "other"

        return {
            "size": info.st_size,
            "created_time": _format_timestamp(info.st_ctime),
            "modified_time": _format_timestamp(info.st_mtime),
            "permissions": oct(stat_module.S_IMODE(info.st_mode)),
            "file_type": file_type,
        }


def _format_timestamp(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat()
