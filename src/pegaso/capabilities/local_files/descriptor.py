"""Self-description for the local_files capability."""

from pegaso.core.descriptor import CapabilityDescriptor, OperationDescriptor

LOCAL_FILES_DESCRIPTOR = CapabilityDescriptor(
    name="local_files",
    domain="Filesystem",
    description=(
        "Safe and consistent interface for exploring and interacting "
        "with a local filesystem."
    ),
    deterministic=True,
    side_effects="Optional (write operations)",
    typical_latency="Very Low",
    network_required=False,
    operations=(
        OperationDescriptor(
            name="list_directory",
            description="Returns the contents of a directory.",
            inputs={"path": "Directory path to list"},
            outputs={
                "directories": "Names of subdirectories",
                "files": "Names of files",
            },
        ),
        OperationDescriptor(
            name="read_file",
            description="Reads the contents of a file.",
            inputs={"path": "File path to read"},
            outputs={
                "content": "File contents",
                "encoding": "Detected or used encoding",
                "size": "File size in bytes",
            },
        ),
        OperationDescriptor(
            name="write_file",
            description="Writes content into a file.",
            inputs={
                "path": "File path to write",
                "content": "Content to write",
                "overwrite": "Whether to overwrite existing file (optional)",
            },
            outputs={"success": "Whether the write succeeded"},
        ),
        OperationDescriptor(
            name="create_directory",
            description="Creates a directory.",
            inputs={"path": "Directory path to create"},
            outputs={"success": "Whether creation succeeded"},
        ),
        OperationDescriptor(
            name="delete",
            description="Deletes a file or directory.",
            inputs={"path": "Path to delete"},
            outputs={"success": "Whether deletion succeeded"},
        ),
        OperationDescriptor(
            name="copy",
            description="Copies a file or directory.",
            inputs={
                "source": "Source path",
                "destination": "Destination path",
            },
            outputs={"success": "Whether copy succeeded"},
        ),
        OperationDescriptor(
            name="move",
            description="Moves a file or directory.",
            inputs={
                "source": "Source path",
                "destination": "Destination path",
            },
            outputs={"success": "Whether move succeeded"},
        ),
        OperationDescriptor(
            name="search",
            description="Searches files by name.",
            inputs={
                "root": "Root directory to search",
                "pattern": "Glob pattern to match",
                "recursive": "Search recursively (optional)",
            },
            outputs={"matching_paths": "Paths matching the pattern"},
        ),
        OperationDescriptor(
            name="grep",
            description="Searches inside file contents.",
            inputs={
                "root": "Root directory to search",
                "query": "Text to search for",
                "recursive": "Search recursively (optional)",
            },
            outputs={
                "matching_files": "Files containing the query",
                "matching_lines": "Matching lines with file and line number",
            },
        ),
        OperationDescriptor(
            name="stat",
            description="Returns metadata for a filesystem object.",
            inputs={"path": "Path to inspect"},
            outputs={
                "size": "Size in bytes",
                "created_time": "Creation timestamp (ISO 8601)",
                "modified_time": "Modification timestamp (ISO 8601)",
                "permissions": "Octal permission string",
                "file_type": "file, directory, or other",
            },
        ),
    ),
)
