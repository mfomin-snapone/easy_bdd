"""
builder_chat.register_chat_routes's tool-call loop must support both
synchronous tool_runner callables (the hand-written per-app tools already
in testrail_builder.py) and async ones (MCP-tool dispatch via
frontend/mcp_tool_bridge.py, since some MCP tools like crawl_device are
async def).
"""

import asyncio
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
