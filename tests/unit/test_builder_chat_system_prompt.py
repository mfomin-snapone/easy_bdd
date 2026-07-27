"""
The chat system prompt's tool-capability note must describe the full MCP
toolset generically (test discovery/validation/running, fixes, device
crawling, Ollama-assisted generation, TestRail read/write) instead of
hard-listing just the two original hand-written tool names — so it doesn't
go stale as frontend/mcp_tool_bridge.py's tool set changes — while keeping
the "only write when explicitly asked" instruction.
"""

from frontend.builder_chat import _CHAT_SYSTEM_PROMPT_TOOLS, _chat_system_prompt


def test_system_prompt_tools_note_no_longer_hardcodes_old_tool_list():
    assert "get_testrail_case" not in _CHAT_SYSTEM_PROMPT_TOOLS
    assert "update_testrail_case" not in _CHAT_SYSTEM_PROMPT_TOOLS


def test_system_prompt_tools_note_keeps_the_explicit_ask_rule():
    lowered = _CHAT_SYSTEM_PROMPT_TOOLS.lower()
    assert "explicitly asked" in lowered


def test_chat_system_prompt_includes_tools_note_only_when_requested():
    with_tools = _chat_system_prompt("ollama", True)
    without_tools = _chat_system_prompt("ollama", False)
    assert _CHAT_SYSTEM_PROMPT_TOOLS.strip() in with_tools
    assert _CHAT_SYSTEM_PROMPT_TOOLS.strip() not in without_tools
