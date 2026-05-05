"""
Skout MCP Server
================
Exposes Skout's discovery, filtering, and outreach capabilities as MCP tools.
Plug this into Claude Desktop, Cursor, Zed — anywhere you want creator lookup
available as a first-class agent tool.

Launch:
    python -m backend.mcp_server.server

Claude Desktop config snippet (mcpServers):
    "skout": {
        "command": "python",
        "args": ["-m", "backend.mcp_server.server"],
        "cwd": "<absolute path to Skout>"
    }
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

from loguru import logger
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from backend.core.database import SessionLocal, init_db
from backend.schemas.agent import (
    DiscoveryRequest,
    FilterRequest,
    Filters,
    OutreachRequest,
)

server = Server("skout")

# Lazy singletons (see backend/api/agents.py for the same pattern).
_singletons: dict = {}


def _discovery():
    if "discovery" not in _singletons:
        from backend.agents.discovery_agent import DiscoveryAgent
        _singletons["discovery"] = DiscoveryAgent()
    return _singletons["discovery"]


def _filtering():
    if "filtering" not in _singletons:
        from backend.agents.filtering_agent import FilteringAgent
        _singletons["filtering"] = FilteringAgent()
    return _singletons["filtering"]


def _outreach():
    if "outreach" not in _singletons:
        from backend.agents.outreach_agent import OutreachAgent
        _singletons["outreach"] = OutreachAgent()
    return _singletons["outreach"]


# ---------- Tool catalog ----------
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="discover_creators",
            description=(
                "Natural-language influencer/creator discovery. "
                "Input a free-form brief (e.g. 'vegan skincare micro-influencers in "
                "Berlin with Gen-Z audience'). Returns ranked creator profiles."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "default": 10, "minimum": 1, "maximum": 50},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="filter_creators",
            description=(
                "Structured-filter creator search. Use when the user specifies "
                "platforms, niches, country, follower range, engagement rate, etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "platforms": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["instagram", "tiktok", "youtube", "facebook", "twitter"]},
                    },
                    "niches": {"type": "array", "items": {"type": "string"}},
                    "languages": {"type": "array", "items": {"type": "string"}},
                    "countries": {"type": "array", "items": {"type": "string"}},
                    "cities": {"type": "array", "items": {"type": "string"}},
                    "min_total_followers": {"type": "integer", "default": 1000},
                    "max_total_followers": {"type": "integer"},
                    "min_engagement_rate": {"type": "number", "default": 0.0},
                    "verified_only": {"type": "boolean", "default": False},
                    "top_k": {"type": "integer", "default": 10},
                },
            },
        ),
        Tool(
            name="draft_outreach",
            description=(
                "Draft a personalized first-touch outreach message to a creator. "
                "Requires a creator_id obtained from one of the search tools."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "creator_id": {"type": "string"},
                    "brand_name": {"type": "string"},
                    "campaign_brief": {"type": "string"},
                    "tone": {"type": "string", "default": "friendly-professional"},
                    "channel": {"type": "string", "enum": ["email", "instagram_dm", "tiktok_dm"], "default": "email"},
                },
                "required": ["creator_id", "brand_name", "campaign_brief"],
            },
        ),
    ]


# ---------- Tool dispatcher ----------
@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    db = SessionLocal()
    try:
        if name == "discover_creators":
            req = DiscoveryRequest(**arguments)
            out = _discovery().run(db, req)
            return [TextContent(type="text", text=out.model_dump_json(indent=2))]

        if name == "filter_creators":
            args = dict(arguments)
            query = args.pop("query", None)
            top_k = args.pop("top_k", 10)
            req = FilterRequest(query=query, filters=Filters(**args), top_k=top_k)
            out = _filtering().run(db, req)
            return [TextContent(type="text", text=out.model_dump_json(indent=2))]

        if name == "draft_outreach":
            req = OutreachRequest(**arguments)
            out = _outreach().draft(db, req)
            return [TextContent(type="text", text=out.model_dump_json(indent=2))]

        return [TextContent(type="text", text=json.dumps({"error": f"unknown tool {name}"}))]
    finally:
        db.close()


# ---------- Entrypoint ----------
async def _main() -> None:
    init_db()
    logger.info("Skout MCP server starting on stdio …")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(_main())
