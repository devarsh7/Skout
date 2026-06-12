"""
Tool-use loop for the SKOUT Brand Agent.

Calls the LLM with tool definitions, executes any returned tool calls,
feeds the results back, and stops when:
  - the LLM returns a final text response (no more tool calls), OR
  - we hit MAX_ITERATIONS.

Returns the final assistant message plus a `tool_trace` array that the
frontend renders as status cards (so users can see the work in real-time).

Uses Groq (OpenAI-compatible API) with llama-3.3-70b-versatile. Falls back
to a plain text reply if Groq is unavailable or tools fail repeatedly.
"""
from __future__ import annotations

import json
from typing import Any

import httpx
from loguru import logger
from sqlalchemy.orm import Session

from backend.agents.tools import (
    TOOL_SCHEMAS,
    execute_tool,
    trace_label,
)
from backend.core.config import settings


MAX_ITERATIONS = 5
MAX_TOKENS     = 800


def run_tool_loop(
    db: Session,
    smb_id: str,
    messages: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    `messages` should already include the system + history + new user turn.
    Returns: {
        "content":     <final assistant text>,
        "tool_trace":  [{"name": str, "args": {...}, "label": str, "result_summary": str}, ...],
    }
    """
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not set.")

    tool_trace: list[dict[str, Any]] = []
    working_messages = list(messages)
    final_text = ""

    for iteration in range(MAX_ITERATIONS):
        resp = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.groq_api_key}",
                "Content-Type":  "application/json",
            },
            json={
                "model":       settings.groq_model,
                "messages":    working_messages,
                "tools":       TOOL_SCHEMAS,
                "tool_choice": "auto",
                "max_tokens":  MAX_TOKENS,
                "temperature": 0.5,
            },
            timeout=45.0,
        )
        resp.raise_for_status()
        data = resp.json()

        choice = data["choices"][0]
        msg = choice["message"]
        tool_calls = msg.get("tool_calls") or []

        # No more tool calls — we're done
        if not tool_calls:
            final_text = (msg.get("content") or "").strip()
            break

        # Add the assistant's tool-call message to history
        working_messages.append({
            "role":       "assistant",
            "content":    msg.get("content") or "",
            "tool_calls": tool_calls,
        })

        # Execute every tool call in this batch
        for tc in tool_calls:
            name = tc["function"]["name"]
            try:
                args = json.loads(tc["function"].get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}

            label = trace_label(name, args)
            logger.debug(f"Tool call: {label}")
            result = execute_tool(db, smb_id, name, args)

            # Summarize for the UI trace (don't dump entire creator lists)
            result_summary = _summarize_result(name, result)
            tool_trace.append({
                "name":           name,
                "args":           args,
                "label":          label,
                "result_summary": result_summary,
            })

            # Feed result back to LLM (truncate huge payloads)
            result_str = json.dumps(result, default=str)
            if len(result_str) > 8000:
                result_str = result_str[:8000] + "…(truncated)"
            working_messages.append({
                "role":         "tool",
                "tool_call_id": tc["id"],
                "name":         name,
                "content":      result_str,
            })

    # If loop exhausted without final text, force one final non-tool turn
    if not final_text:
        try:
            resp = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.groq_api_key}",
                    "Content-Type":  "application/json",
                },
                json={
                    "model":       settings.groq_model,
                    "messages":    working_messages + [
                        {"role": "user", "content": "Now summarize your findings for me in 3-4 sentences with one clear next step."}
                    ],
                    "max_tokens":  MAX_TOKENS,
                    "temperature": 0.5,
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            final_text = resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            logger.warning(f"Final summarize failed: {exc}")
            final_text = (
                "I gathered the data but couldn't compose a final summary. "
                "Try asking again with a more specific ask."
            )

    return {
        "content":    final_text,
        "tool_trace": tool_trace,
    }


def _summarize_result(name: str, result: dict) -> str:
    """Short string for UI status cards — never the full JSON."""
    if not isinstance(result, dict):
        return "ok"
    if "error" in result:
        return f"error: {result['error']}"

    if name == "discover_creators":
        n = result.get("count", 0)
        return f"Found {n} match{'es' if n != 1 else ''}"
    if name == "filter_creators":
        return f"{result.get('count', 0)} kept after filter"
    if name == "get_creator_profile":
        return f"Loaded {result.get('name', 'creator')}"
    if name == "draft_outreach_message":
        return f"Drafted message to {result.get('creator_name', 'creator')}"
    if name == "get_campaign_status":
        return f"{result.get('count', 0)} campaign(s) loaded"
    if name == "get_local_benchmark":
        n = result.get("creator_count", 0)
        return f"{n} creators in that segment"
    if name == "save_brand_fact":
        return "Saved to memory"
    return "ok"
