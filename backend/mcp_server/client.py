"""
Thin Python client that spawns the Skout MCP server over stdio and calls
its tools. Handy for smoke-testing or internal agents that want to use the
MCP contract instead of importing the agents directly.

Example:
    import asyncio
    from backend.mcp_server.client import SkoutMCPClient

    async def main():
        async with SkoutMCPClient() as client:
            print(await client.call("discover_creators", {"query": "fitness"}))

    asyncio.run(main())
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@asynccontextmanager
async def skout_mcp_session():
    params = StdioServerParameters(command="python", args=["-m", "backend.mcp_server.server"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


class SkoutMCPClient:
    """Context-manager wrapper around an MCP stdio session."""

    def __init__(self) -> None:
        self._cm = None
        self._session: ClientSession | None = None

    async def __aenter__(self) -> "SkoutMCPClient":
        self._cm = skout_mcp_session()
        self._session = await self._cm.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._cm.__aexit__(exc_type, exc, tb)

    async def list_tools(self):
        return await self._session.list_tools()

    async def call(self, tool: str, arguments: dict) -> str:
        result = await self._session.call_tool(tool, arguments)
        # MCP returns a list of content items; concatenate the text ones.
        return "\n".join(item.text for item in result.content if getattr(item, "text", None))
