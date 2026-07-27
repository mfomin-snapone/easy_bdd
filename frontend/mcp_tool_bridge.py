"""Bridge from the Easy BDD MCP tool registry to the builder chat assistants.

Both frontend/testrail_builder.py and frontend/local_builder.py embed an
Ollama/GitHub-Models chat assistant (frontend/builder_chat.py) that calls
tools via OpenAI-style function-calling. This module exposes every
@mcp.tool() registered in easybdd/mcp_server.py to those assistants, so new
MCP tools are automatically available in chat with no changes to either
builder app.
"""

from __future__ import annotations

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
    """
    try:
        result = await mcp.call_tool(name, args)
    except Exception as exc:  # noqa: BLE001 - reported to the model, not raised
        return json.dumps({"error": str(exc)})
    return _stringify_tool_result(result)
