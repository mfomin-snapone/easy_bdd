"""
The chat system prompt's tool-capability note must describe the full MCP
toolset generically (test discovery/validation/running, fixes, device
crawling, Ollama-assisted generation, TestRail read/write) instead of
hard-listing just the two original hand-written tool names — so it doesn't
go stale as frontend/mcp_tool_bridge.py's tool set changes — while keeping
the "only write when explicitly asked" instruction.
"""

import importlib.util
import sys
from pathlib import Path

_FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


def _load_frontend_sibling_module(name: str) -> None:
    """Register frontend/<name>.py as a top-level module in sys.modules.

    frontend/builder_chat.py (and frontend/builder_core.py, which it in
    turn imports) use bare same-directory imports (e.g. ``from
    builder_core import CATALOG``) rather than ``frontend.``-qualified
    ones, matching how they are loaded in production by
    frontend/testrail_builder.py and frontend/local_builder.py -- each of
    which inserts the frontend/ directory onto sys.path before importing
    them. Doing the same repo-wide sys.path insertion here (e.g. via a
    tests/conftest.py loaded for every test under tests/) is unnecessary
    for this one module and risky: frontend/mcp_server.py and
    easybdd/mcp_server.py share a basename, so a bare `import mcp_server`
    anywhere else in the suite would silently resolve to whichever one
    sys.path insertion order favors. Registering just the modules this
    test actually needs directly in sys.modules avoids that.
    """
    if name in sys.modules:
        return
    spec = importlib.util.spec_from_file_location(name, _FRONTEND_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)


_load_frontend_sibling_module("action_definitions")
_load_frontend_sibling_module("builder_core")

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
