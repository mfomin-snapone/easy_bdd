"""
builder_chat.register_chat_routes's tool-call loop must support both
synchronous tool_runner callables (the hand-written per-app tools already
in testrail_builder.py) and async ones (MCP-tool dispatch via
frontend/mcp_tool_bridge.py, since some MCP tools like crawl_device are
async def).
"""

import asyncio

from frontend.builder_chat import _invoke_tool_runner


def test_invoke_tool_runner_supports_sync_runner():
    def sync_runner(name, args):
        return f"sync:{name}:{args}"

    result = asyncio.run(_invoke_tool_runner(sync_runner, "get_testrail_case", {"case_id": 1}))
    assert result == "sync:get_testrail_case:{'case_id': 1}"


def test_invoke_tool_runner_supports_async_runner():
    async def async_runner(name, args):
        return f"async:{name}:{args}"

    result = asyncio.run(_invoke_tool_runner(async_runner, "list_tests", {}))
    assert result == "async:list_tests:{}"


def test_invoke_tool_runner_handles_missing_runner():
    result = asyncio.run(_invoke_tool_runner(None, "anything", {}))
    assert "error" in result.lower()
