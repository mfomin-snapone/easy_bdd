"""
frontend/testrail_builder.py's chat assistant must expose both its two
hand-written TestRail tools (get_testrail_case, update_testrail_case) and
every MCP tool from easybdd/mcp_server.py, and route calls for MCP-only
tool names to the MCP bridge instead of returning "Unknown tool".
"""

import asyncio
import json

from frontend.mcp_tool_bridge import list_mcp_tool_defs
from frontend.testrail_builder import ALL_CHAT_TOOLS, TESTRAIL_CHAT_TOOLS, _run_chat_tool


def test_all_chat_tools_includes_hand_written_and_mcp_tools():
    names = {t["function"]["name"] for t in ALL_CHAT_TOOLS}
    hand_written_names = {t["function"]["name"] for t in TESTRAIL_CHAT_TOOLS}
    mcp_names = {t["function"]["name"] for t in list_mcp_tool_defs()}

    assert hand_written_names <= names
    assert mcp_names <= names
    assert names == hand_written_names | mcp_names
    assert len(ALL_CHAT_TOOLS) == len(names)


def test_run_chat_tool_dispatches_mcp_only_tool_by_name():
    result = asyncio.run(_run_chat_tool("list_tests", {"path": "tests/cases"}))
    assert isinstance(result, str)
    assert result.strip() != ""
    assert "Unknown tool" not in result
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert "TextContent(" not in result


def test_run_chat_tool_still_reports_unknown_tool_for_bogus_name():
    result = asyncio.run(_run_chat_tool("definitely_not_a_tool", {}))
    assert "error" in result.lower()
