"""Standard error types for PEGASO capabilities."""


class CapabilityError(Exception):
    """Base error for capability operations."""


class PathAccessError(CapabilityError):
    """Raised when a path is outside the allowed filesystem scope."""
