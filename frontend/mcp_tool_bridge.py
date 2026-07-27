"""Bridge from the Easy BDD MCP tool registry to the builder chat assistants.

Both frontend/testrail_builder.py and frontend/local_builder.py embed an
Ollama/GitHub-Models chat assistant (frontend/builder_chat.py) that calls
tools via OpenAI-style function-calling. This module exposes every
@mcp.tool() registered in easybdd/mcp_server.py to those assistants, so new
MCP tools are automatically available in chat with no changes to either
builder app.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List

from easybdd.mcp_server import mcp


def list_mcp_tool_defs() -> List[Dict[str, Any]]:
    """OpenAI/Ollama-style tool schemas for every registered MCP tool."""
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.parameters,
            },
        }
        for tool in mcp._tool_manager.list_tools()
    ]


def _stringify_tool_result(result: Any) -> str:
    # FastMCP's call_tool() returns a (content_blocks, structured_dict) 2-tuple
    # for any tool with an output schema -- which is every tool here, since
    # all 20 are annotated `-> str`. Prefer the structured side: functions
    # returning a single str get wrapped as {"result": "..."} by FastMCP: unwrap
    # that back to the plain string; anything else, re-serialize the dict.
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], dict):
        structured = result[1]
        if set(structured) == {"result"}:
            return str(structured["result"])
        return json.dumps(structured)
    if isinstance(result, dict):
        return json.dumps(result)
    if isinstance(result, (list, tuple)):
        parts = []
        for block in result:
            text = getattr(block, "text", None)
            parts.append(text if text is not None else str(block))
        return "\n".join(parts)
    return str(result)


async def run_mcp_tool(name: str, args: Dict[str, Any]) -> str:
    """Invoke an MCP tool by name, returning a JSON-string-safe result.

    Never raises — errors come back as a JSON error string so the chat
    model sees them as tool output, matching the existing hand-written
    tool runners' behavior.

    Both apps are long-lived FastAPI/uvicorn processes serving all users off
    one event loop. 19 of the 20 MCP tools are plain `def` (sync) and
    `mcp.call_tool()` runs them inline with no thread offload, so a slow sync
    tool (run_tests, probe_selector, ollama_generate_tests, ...) would freeze
    the whole process for every user for the call's duration. To avoid that,
    the entire call_tool() coroutine is driven to completion on a separate
    worker thread via asyncio.to_thread(asyncio.run, ...): a new thread has no
    running event loop of its own, so asyncio.run() there does not conflict
    with the loop this coroutine is already running on, and it works
    identically for sync-bodied and async-bodied (e.g. crawl_device) tools --
    verified manually against list_tests (a sync tool) with a concurrent
    sibling task to confirm the outer loop stays responsive.
    """
    try:
        result = await asyncio.to_thread(asyncio.run, mcp.call_tool(name, args))
    except Exception as exc:  # noqa: BLE001 - reported to the model, not raised
        return json.dumps({"error": str(exc)})
    return _stringify_tool_result(result)
