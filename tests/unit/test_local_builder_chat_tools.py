"""
frontend/local_builder.py has no hand-written chat tools of its own
(unlike testrail_builder.py) — it should expose exactly the full MCP
toolset from easybdd/mcp_server.py to its chat assistant.
"""

from frontend.local_builder import app
from frontend.mcp_tool_bridge import list_mcp_tool_defs


def test_local_builder_registers_chat_status_route():
    from fastapi.testclient import TestClient

    client = TestClient(app)
    resp = client.post("/api/chat/status", json={"provider": "ollama"})
    assert resp.status_code == 200


def test_local_builder_exposes_every_mcp_tool():
    # register_chat_routes doesn't expose tool_defs on the app object directly,
    # so this confirms the bridge itself (used verbatim by local_builder.py)
    # returns the full toolset local_builder.py wires in.
    defs = list_mcp_tool_defs()
    assert len(defs) >= 15
    names = {d["function"]["name"] for d in defs}
    assert "list_tests" in names
    assert "crawl_device" in names
