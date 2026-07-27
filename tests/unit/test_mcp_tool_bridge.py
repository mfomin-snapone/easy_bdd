"""
frontend/mcp_tool_bridge.py exposes every Easy BDD MCP tool
(@mcp.tool() functions in easybdd/mcp_server.py) as an OpenAI-style
function-calling schema, and can invoke any of them by name, so the
builder chat assistants (frontend/testrail_builder.py,
frontend/local_builder.py) can call the full toolset instead of a couple
of hand-written ones.
"""

import asyncio
import json

from easybdd.mcp_server import mcp
from frontend.mcp_tool_bridge import _short_description, list_mcp_tool_defs, run_mcp_tool


def test_list_mcp_tool_defs_covers_every_registered_tool():
    expected_names = {tool.name for tool in mcp._tool_manager.list_tools()}
    defs = list_mcp_tool_defs()
    names = {d["function"]["name"] for d in defs}

    assert names == expected_names
    assert len(expected_names) >= 15  # sanity: full toolset, not a subset


def test_list_mcp_tool_defs_schema_shape():
    defs = list_mcp_tool_defs()
    assert defs, "no tool defs returned"
    for d in defs:
        assert d["type"] == "function"
        fn = d["function"]
        assert fn["name"]
        assert isinstance(fn["parameters"], dict)


def test_run_mcp_tool_invokes_real_tool_and_returns_text():
    result = asyncio.run(run_mcp_tool("list_tests", {"path": "tests/cases"}))
    assert isinstance(result, str)
    assert result.strip() != ""
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert "TextContent(" not in result


def test_run_mcp_tool_unknown_tool_returns_error_not_exception():
    result = asyncio.run(run_mcp_tool("not_a_real_tool", {}))
    assert isinstance(result, str)
    assert "error" in result.lower()


def test_short_description_cuts_before_numpydoc_parameters_section():
    doc = "One-line summary.\n\nParameters\n----------\npath : a long explanation\n" * 5
    assert _short_description(doc) == "One-line summary."


def test_short_description_falls_back_when_no_summary_precedes_parameters():
    # crawl_device's docstring has no summary line -- it starts directly
    # with "Parameters\n----------", which would otherwise cut to an empty
    # string. Must fall back to non-empty, capped text instead.
    doc = "Parameters\n----------\n" + ("url : very long explanation " * 20)
    result = _short_description(doc)
    assert result != ""
    assert len(result) <= 200


def test_short_description_is_always_capped_and_single_line():
    defs = list_mcp_tool_defs()
    for d in defs:
        description = d["function"]["description"]
        assert len(description) <= 200
        assert "\n" not in description
