"""Self-description for the git capability."""

from pegaso.core.descriptor import CapabilityDescriptor, OperationDescriptor

GIT_DESCRIPTOR = CapabilityDescriptor(
    name="git",
    domain="Version Control",
    description=(
        "Consistent interface for Git repository operations. "
        "Implementation may be local or MCP-backed."
    ),
    deterministic=False,
    side_effects="Common (most operations mutate repository state)",
    typical_latency="Low",
    network_required=False,
    metadata={"preferred_backend": "mcp-server-git"},
    operations=(
        OperationDescriptor(
            name="status",
            description="Shows the working tree status.",
            inputs={},
            outputs={"output": "Git status text"},
        ),
        OperationDescriptor(
            name="diff",
            description="Shows repository diffs.",
            inputs={
                "staged": "Whether to show staged changes (optional)",
                "target": "Branch or commit to compare against (optional)",
                "context_lines": "Number of context lines (optional)",
            },
            outputs={"output": "Diff text"},
        ),
        OperationDescriptor(
            name="add",
            description="Stages files for commit.",
            inputs={"files": "Paths to stage"},
            outputs={
                "success": "Whether staging succeeded",
                "output": "Command output",
            },
        ),
        OperationDescriptor(
            name="commit",
            description="Records staged changes.",
            inputs={"message": "Commit message"},
            outputs={
                "success": "Whether the commit succeeded",
                "commit_hash": "New commit hash when available",
                "output": "Command output",
            },
        ),
        OperationDescriptor(
            name="checkout",
            description="Switches branches.",
            inputs={"branch": "Branch name to checkout"},
            outputs={
                "success": "Whether checkout succeeded",
                "output": "Command output",
            },
        ),
        OperationDescriptor(
            name="branch",
            description="Lists or creates branches.",
            inputs={
                "name": "Branch name when creating (optional)",
                "create": "Whether to create a branch (optional)",
                "base_branch": "Base branch for creation (optional)",
                "branch_type": "local, remote, or all when listing (optional)",
            },
            outputs={
                "branches": "Listed branch names when listing",
                "success": "Whether branch creation succeeded",
                "output": "Command output",
            },
        ),
        OperationDescriptor(
            name="log",
            description="Shows commit history.",
            inputs={
                "max_count": "Maximum number of commits (optional)",
                "start_timestamp": "Start timestamp filter (optional)",
                "end_timestamp": "End timestamp filter (optional)",
            },
            outputs={
                "commits": "Structured commit entries",
                "output": "Raw log text",
            },
        ),
        OperationDescriptor(
            name="show",
            description="Shows a revision.",
            inputs={"revision": "Commit hash, branch, or tag"},
            outputs={"output": "Revision details"},
        ),
        OperationDescriptor(
            name="pull",
            description="Fetches and merges remote changes.",
            inputs={
                "remote": "Remote name (optional)",
                "branch": "Branch name (optional)",
            },
            outputs={
                "success": "Whether pull succeeded",
                "output": "Command output",
            },
        ),
        OperationDescriptor(
            name="push",
            description="Publishes commits to a remote.",
            inputs={
                "remote": "Remote name (optional)",
                "branch": "Branch name (optional)",
            },
            outputs={
                "success": "Whether push succeeded",
                "output": "Command output",
            },
        ),
        OperationDescriptor(
            name="clone",
            description="Clones a remote repository.",
            inputs={
                "url": "Repository URL",
                "destination": "Destination path",
            },
            outputs={
                "success": "Whether clone succeeded",
                "output": "Command output",
            },
        ),
    ),
)
