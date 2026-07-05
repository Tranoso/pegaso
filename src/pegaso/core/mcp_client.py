"""Minimal MCP stdio client for capability backends."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class McpServerConfig:
    """Configuration for launching an MCP server over stdio."""

    command: str
    args: tuple[str, ...] = ()
    env: dict[str, str] | None = None


def call_mcp_tool(
    server: McpServerConfig,
    tool_name: str,
    arguments: dict[str, Any],
) -> str:
    """Invoke an MCP tool and return the primary text response."""

    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as exc:
        raise ImportError(
            "The 'mcp' package is required for MCP-backed capabilities. "
            "Install with: pip install 'pegaso[git-mcp]'"
        ) from exc

    async def _call() -> str:
        server_params = StdioServerParameters(
            command=server.command,
            args=list(server.args),
            env=server.env,
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                if result.isError:
                    message = _extract_text(result.content)
                    raise RuntimeError(message or f"MCP tool failed: {tool_name}")
                return _extract_text(result.content)

    return asyncio.run(_call())


def _extract_text(content: Any) -> str:
    if not content:
        return ""
    first = content[0]
    text = getattr(first, "text", None)
    return text if isinstance(text, str) else str(first)
