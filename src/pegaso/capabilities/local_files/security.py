"""Path sandboxing for safe filesystem access."""

from __future__ import annotations

from pathlib import Path

from pegaso.core.errors import PathAccessError


class PathGuard:
    """Restrict filesystem access to allowed root directories."""

    def __init__(self, allowed_roots: list[str | Path]) -> None:
        if not allowed_roots:
            raise ValueError("At least one allowed root must be provided")
        self._roots = [Path(root).resolve() for root in allowed_roots]

    @property
    def roots(self) -> tuple[Path, ...]:
        return tuple(self._roots)

    def resolve(self, path: str | Path) -> Path:
        """Resolve and validate a path against allowed roots."""
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = self._roots[0] / candidate

        resolved = candidate.resolve()

        for root in self._roots:
            try:
                resolved.relative_to(root)
                return resolved
            except ValueError:
                continue

        roots_display = ", ".join(str(root) for root in self._roots)
        raise PathAccessError(
            f"Path '{path}' is outside allowed roots: {roots_display}"
        )
