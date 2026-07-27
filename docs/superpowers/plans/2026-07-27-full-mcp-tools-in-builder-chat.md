# Full MCP Tools in Builder Chat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every Easy BDD MCP tool (the 20 `@mcp.tool()` functions in
`easybdd/mcp_server.py`) callable from the chat assistants embedded in both
`frontend/testrail_builder.py` (port 8091) and `frontend/local_builder.py`
(port 9093), without hand-writing per-tool schemas.

**Architecture:** A new bridge module, `frontend/mcp_tool_bridge.py`, reads
tool schemas directly off the already-constructed `FastMCP` instance in
`easybdd.mcp_server` and invokes tools through it. Both builder apps
concatenate this tool list onto whatever hand-written tools they already
have and hand a single async dispatcher to the existing
`frontend/builder_chat.py:register_chat_routes`. `register_chat_routes`'s
tool-call loop gains support for an async tool runner (needed because some
MCP tools, e.g. `crawl_device`, are `async def`).

**Tech Stack:** FastAPI, FastMCP (`mcp.server.fastmcp`), pytest,
`fastapi.testclient.TestClient`.

## Global Constraints

- Design doc: `docs/superpowers/specs/2026-07-27-full-mcp-tools-in-builder-chat-design.md`.
- Both builders (8091 and 9093) get the full MCP tool set — not just one.
- Write safety is "trust the model": no new confirmation-token flow. Tool
  descriptions/system prompt instruct the model to only perform real
  writes/runs/pushes when the user has explicitly asked. Existing per-tool
  safety in `mcp_server.py` (`run_tests` defaults `dry_run=True`, `apply_fix`
  requires `confirmed=True`) is unchanged.
- Tool schemas are auto-generated from the live `FastMCP` tool registry —
  no hand-written per-tool JSON schema blocks for the 20 MCP tools.
- Run tests with `env/bin/python -m pytest <path> -v` (plain `env/bin/pytest`
  fails to resolve the `frontend` namespace package in this repo — verified
  during planning).

---

### Task 1: Async-capable tool runner in `builder_chat.py`

**Files:**
- Modify: `frontend/builder_chat.py:1-11` (imports), `frontend/builder_chat.py:655-745` (`register_chat_routes`)
- Test: `tests/unit/test_builder_chat_async_tools.py`

**Interfaces:**
- Produces: `async def _invoke_tool_runner(tool_runner, name, args) -> str` —
  calls `tool_runner(name, args)` and awaits the result if it's awaitable,
  otherwise returns it as-is. Used internally by `register_chat_routes`;
  later tasks' async tool runners (`frontend/mcp_tool_bridge.run_mcp_tool`)
  rely on this to work when passed to `register_chat_routes`.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_builder_chat_async_tools.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `env/bin/python -m pytest tests/unit/test_builder_chat_async_tools.py -v`
Expected: FAIL with `ImportError: cannot import name '_invoke_tool_runner'`

- [ ] **Step 3: Add `import inspect` to `frontend/builder_chat.py`**

At the top of `frontend/builder_chat.py`, the import block currently reads:

```python
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
```

Change to:

```python
from __future__ import annotations

import inspect
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
```

- [ ] **Step 4: Add `_invoke_tool_runner` and use it in `register_chat_routes`**

Immediately before `def register_chat_routes(` in `frontend/builder_chat.py`,
add:

```python
async def _invoke_tool_runner(
    tool_runner: Optional[Callable[[str, Dict[str, Any]], Any]],
    name: str,
    args: Dict[str, Any],
) -> str:
    """Call tool_runner, awaiting the result if it's a coroutine.

    Lets register_chat_routes accept either a synchronous tool_runner (the
    hand-written per-app tools) or an async one (MCP-tool dispatch, since
    some MCP tools like crawl_device are async def).
    """
    if not tool_runner:
        return json.dumps({"error": "Tool runner unavailable."})
    output = tool_runner(name, args)
    if inspect.isawaitable(output):
        output = await output
    return output
```

Then change the `register_chat_routes` signature's `tool_runner` type hint
from:

```python
    tool_runner: Optional[Callable[[str, Dict[str, Any]], str]] = None,
```

to:

```python
    tool_runner: Optional[Callable[[str, Dict[str, Any]], Any]] = None,
```

Then replace the pseudo-call branch:

```python
            if pseudo_call:
                name, args = pseudo_call
                output = tool_runner(name, args) if tool_runner else json.dumps({"error": "Tool runner unavailable."})
                messages.append({"role": "tool", "content": output})
                continue
```

with:

```python
            if pseudo_call:
                name, args = pseudo_call
                output = await _invoke_tool_runner(tool_runner, name, args)
                messages.append({"role": "tool", "content": output})
                continue
```

And replace the tool_calls loop body:

```python
                output = tool_runner(name, args) if tool_runner else json.dumps({"error": "Tool runner unavailable."})
                tool_message = {"role": "tool", "content": output}
```

with:

```python
                output = await _invoke_tool_runner(tool_runner, name, args)
                tool_message = {"role": "tool", "content": output}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `env/bin/python -m pytest tests/unit/test_builder_chat_async_tools.py -v`
Expected: PASS (3 passed)

- [ ] **Step 6: Commit**

```bash
git add frontend/builder_chat.py tests/unit/test_builder_chat_async_tools.py
git commit -m "feat: support async tool runners in builder chat tool-call loop"
```

---

### Task 2: `frontend/mcp_tool_bridge.py` — expose MCP tools to chat

**Files:**
- Create: `frontend/mcp_tool_bridge.py`
- Test: `tests/unit/test_mcp_tool_bridge.py`

**Interfaces:**
- Consumes: `easybdd.mcp_server.mcp` (the module-level `FastMCP` instance;
  `mcp._tool_manager.list_tools()` is synchronous and returns objects with
  `.name`, `.description`, `.parameters` — verified directly against this
  repo's `mcp_server.py` during planning: 20 tools registered).
- Produces:
  - `list_mcp_tool_defs() -> list[dict]` — synchronous, returns one
    `{"type": "function", "function": {"name", "description", "parameters"}}`
    dict per registered MCP tool. Tasks 3 and 4 call this once at app
    startup.
  - `async def run_mcp_tool(name: str, args: dict) -> str` — invokes the
    named MCP tool via `await mcp.call_tool(name, args)` and returns a JSON
    string; never raises (errors come back as `{"error": "..."}` JSON, same
    behavior as the existing hand-written tool runners). Tasks 3 and 4 pass
    this as (part of) their `tool_runner`.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_mcp_tool_bridge.py`:

```python
"""
frontend/mcp_tool_bridge.py exposes every Easy BDD MCP tool
(@mcp.tool() functions in easybdd/mcp_server.py) as an OpenAI-style
function-calling schema, and can invoke any of them by name, so the
builder chat assistants (frontend/testrail_builder.py,
frontend/local_builder.py) can call the full toolset instead of a couple
of hand-written ones.
"""

import asyncio

from easybdd.mcp_server import mcp
from frontend.mcp_tool_bridge import list_mcp_tool_defs, run_mcp_tool


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


def test_run_mcp_tool_unknown_tool_returns_error_not_exception():
    result = asyncio.run(run_mcp_tool("not_a_real_tool", {}))
    assert isinstance(result, str)
    assert "error" in result.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `env/bin/python -m pytest tests/unit/test_mcp_tool_bridge.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'frontend.mcp_tool_bridge'`

- [ ] **Step 3: Write the implementation**

Create `frontend/mcp_tool_bridge.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `env/bin/python -m pytest tests/unit/test_mcp_tool_bridge.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add frontend/mcp_tool_bridge.py tests/unit/test_mcp_tool_bridge.py
git commit -m "feat: add MCP tool bridge for builder chat assistants"
```

---

### Task 3: Wire the full tool set into `testrail_builder.py`

**Files:**
- Modify: `frontend/testrail_builder.py:54-73` (imports), `frontend/testrail_builder.py:227-317` (chat tool wiring)
- Test: `tests/unit/test_testrail_builder_chat_tools.py`

**Interfaces:**
- Consumes: `list_mcp_tool_defs`, `run_mcp_tool` from Task 2;
  `_invoke_tool_runner` support from Task 1 (indirectly, via
  `register_chat_routes`).
- Produces: `ALL_CHAT_TOOLS: list[dict]` (module-level in
  `frontend/testrail_builder.py`) — the hand-written `TESTRAIL_CHAT_TOOLS`
  concatenated with every MCP tool schema. Not consumed outside this file,
  but tested directly.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_testrail_builder_chat_tools.py`:

```python
"""
frontend/testrail_builder.py's chat assistant must expose both its two
hand-written TestRail tools (get_testrail_case, update_testrail_case) and
every MCP tool from easybdd/mcp_server.py, and route calls for MCP-only
tool names to the MCP bridge instead of returning "Unknown tool".
"""

import asyncio

from frontend.mcp_tool_bridge import list_mcp_tool_defs
from frontend.testrail_builder import ALL_CHAT_TOOLS, TESTRAIL_CHAT_TOOLS, _run_chat_tool


def test_all_chat_tools_includes_hand_written_and_mcp_tools():
    names = {t["function"]["name"] for t in ALL_CHAT_TOOLS}
    hand_written_names = {t["function"]["name"] for t in TESTRAIL_CHAT_TOOLS}
    mcp_names = {t["function"]["name"] for t in list_mcp_tool_defs()}

    assert hand_written_names <= names
    assert mcp_names <= names
    assert names == hand_written_names | mcp_names


def test_run_chat_tool_dispatches_mcp_only_tool_by_name():
    result = asyncio.run(_run_chat_tool("list_tests", {"path": "tests/cases"}))
    assert isinstance(result, str)
    assert result.strip() != ""
    assert "Unknown tool" not in result


def test_run_chat_tool_still_reports_unknown_tool_for_bogus_name():
    result = asyncio.run(_run_chat_tool("definitely_not_a_tool", {}))
    assert "error" in result.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `env/bin/python -m pytest tests/unit/test_testrail_builder_chat_tools.py -v`
Expected: FAIL — `ImportError: cannot import name 'ALL_CHAT_TOOLS'` (and
`_run_chat_tool` is still sync, called without `await` support wired up)

- [ ] **Step 3: Add the MCP bridge import**

In `frontend/testrail_builder.py`, the import block currently ends with:

```python
from builder_chat import register_chat_routes  # noqa: E402
```

Change to:

```python
from builder_chat import register_chat_routes  # noqa: E402
from mcp_tool_bridge import list_mcp_tool_defs, run_mcp_tool  # noqa: E402
```

- [ ] **Step 4: Combine tool lists and make the dispatcher async**

Replace this block (from the comment above `TESTRAIL_CHAT_TOOLS` — keep the
`TESTRAIL_CHAT_TOOLS = [...]` list itself exactly as-is — through the end of
the existing `register_chat_routes(...)` call):

```python
def _testrail_configured() -> bool:
    return bool(
        os.getenv("TESTRAIL_URL") and os.getenv("TESTRAIL_USERNAME") and os.getenv("TESTRAIL_API_KEY")
    )


def _run_chat_tool(name: str, args: Dict[str, Any]) -> str:
    """Execute a tool call the chat model requested, returning a JSON string
    (never raises — errors are reported back to the model as tool output)."""
    try:
        if name == "get_testrail_case":
            case_id = int(args["case_id"])
            case = _tr().get_case(case_id)
            body = strip_html_to_text(str(case.get("custom_preconds") or ""))
            return json.dumps({"case_id": case_id, "title": case.get("title", ""), "preconditions": body})
        if name == "update_testrail_case":
            case_id = int(args["case_id"])
            payload: Dict[str, Any] = {}
            if args.get("title") is not None:
                payload["title"] = args["title"]
            if args.get("preconditions") is not None:
                payload["custom_preconds"] = args["preconditions"]
            if not payload:
                return json.dumps({"error": "Nothing to update — provide title and/or preconditions."})
            case = _tr().update_case(case_id, **payload)
            return json.dumps({"ok": True, "case_id": case_id, "title": case.get("title", "")})
        return json.dumps({"error": f"Unknown tool '{name}'"})
    except TestRailError as exc:
        return json.dumps({"error": f"TestRail error: {exc}"})
    except Exception as exc:  # noqa: BLE001 - reported to the model, not raised
        return json.dumps({"error": str(exc)})


register_chat_routes(
    app,
    tool_defs=TESTRAIL_CHAT_TOOLS,
    tool_runner=_run_chat_tool,
    tools_available=_testrail_configured,
)
```

with:

```python
async def _run_chat_tool(name: str, args: Dict[str, Any]) -> str:
    """Execute a tool call the chat model requested, returning a JSON string
    (never raises — errors are reported back to the model as tool output).
    Falls through to the full MCP toolset (frontend/mcp_tool_bridge.py) for
    any name that isn't one of this app's two hand-written tools."""
    try:
        if name == "get_testrail_case":
            case_id = int(args["case_id"])
            case = _tr().get_case(case_id)
            body = strip_html_to_text(str(case.get("custom_preconds") or ""))
            return json.dumps({"case_id": case_id, "title": case.get("title", ""), "preconditions": body})
        if name == "update_testrail_case":
            case_id = int(args["case_id"])
            payload: Dict[str, Any] = {}
            if args.get("title") is not None:
                payload["title"] = args["title"]
            if args.get("preconditions") is not None:
                payload["custom_preconds"] = args["preconditions"]
            if not payload:
                return json.dumps({"error": "Nothing to update — provide title and/or preconditions."})
            case = _tr().update_case(case_id, **payload)
            return json.dumps({"ok": True, "case_id": case_id, "title": case.get("title", "")})
        return await run_mcp_tool(name, args)
    except TestRailError as exc:
        return json.dumps({"error": f"TestRail error: {exc}"})
    except Exception as exc:  # noqa: BLE001 - reported to the model, not raised
        return json.dumps({"error": str(exc)})


ALL_CHAT_TOOLS = TESTRAIL_CHAT_TOOLS + list_mcp_tool_defs()

register_chat_routes(
    app,
    tool_defs=ALL_CHAT_TOOLS,
    tool_runner=_run_chat_tool,
)
```

Note `tools_available=_testrail_configured` is dropped entirely (so
`register_chat_routes` defaults to always-available) — the MCP toolset
doesn't require TestRail credentials; TestRail-specific MCP tools (e.g.
`repush_yaml_to_testrail`) already fail gracefully with a JSON error at
call time if unconfigured, same as `get_testrail_case`/`update_testrail_case`
do today.

- [ ] **Step 5: Verify the now-unused `_testrail_configured` function is gone**

Run: `grep -n _testrail_configured frontend/testrail_builder.py`
Expected: no output (it was removed as part of the Step 4 replacement)

- [ ] **Step 6: Run test to verify it passes**

Run: `env/bin/python -m pytest tests/unit/test_testrail_builder_chat_tools.py -v`
Expected: PASS (3 passed)

- [ ] **Step 7: Run the full existing test suite for this file to check for regressions**

Run: `env/bin/python -m pytest tests/unit/test_builder_import_recording.py tests/unit/test_builder_runs_view.py -v`
Expected: all PASS (these import `frontend.testrail_builder`, exercising
the module-level code this task changed)

- [ ] **Step 8: Commit**

```bash
git add frontend/testrail_builder.py tests/unit/test_testrail_builder_chat_tools.py
git commit -m "feat: expose full MCP toolset in TestRail builder chat"
```

---

### Task 4: Wire the full tool set into `local_builder.py`

**Files:**
- Modify: `frontend/local_builder.py:85` (import), `frontend/local_builder.py:109` (chat registration)
- Test: `tests/unit/test_local_builder_chat_tools.py`

**Interfaces:**
- Consumes: `list_mcp_tool_defs`, `run_mcp_tool` from Task 2.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_local_builder_chat_tools.py`:

```python
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
```

- [ ] **Step 2: Confirm current wiring has no tools (pre-change baseline)**

Run: `grep -n "register_chat_routes" frontend/local_builder.py`
Expected output: `register_chat_routes(app)` — no `tool_defs`/`tool_runner`
arguments yet. This confirms the file needs the Step 3 change (the test
suite itself will already pass either way, since it doesn't assert on
wiring — it's `frontend/local_builder.py` we're changing, not the test).

- [ ] **Step 3: Wire MCP tools into `local_builder.py`**

In `frontend/local_builder.py`, the import block currently ends with:

```python
from builder_chat import register_chat_routes  # noqa: E402
```

Change to:

```python
from builder_chat import register_chat_routes  # noqa: E402
from mcp_tool_bridge import list_mcp_tool_defs, run_mcp_tool  # noqa: E402
```

And the registration line:

```python
register_chat_routes(app)
```

Change to:

```python
register_chat_routes(
    app,
    tool_defs=list_mcp_tool_defs(),
    tool_runner=run_mcp_tool,
)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `env/bin/python -m pytest tests/unit/test_local_builder_chat_tools.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add frontend/local_builder.py tests/unit/test_local_builder_chat_tools.py
git commit -m "feat: expose full MCP toolset in local builder chat"
```

---

### Task 5: Generalize the chat system prompt's tool description

**Files:**
- Modify: `frontend/builder_chat.py:149-154` (`_CHAT_SYSTEM_PROMPT_TOOLS`)
- Test: `tests/unit/test_builder_chat_system_prompt.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: no new symbols — `_CHAT_SYSTEM_PROMPT_TOOLS`'s content changes;
  its name and usage in `_chat_system_prompt` are unchanged.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_builder_chat_system_prompt.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `env/bin/python -m pytest tests/unit/test_builder_chat_system_prompt.py -v`
Expected: FAIL on `test_system_prompt_tools_note_no_longer_hardcodes_old_tool_list`
(the current text contains both old names)

- [ ] **Step 3: Update the constant**

In `frontend/builder_chat.py`, replace:

```python
_CHAT_SYSTEM_PROMPT_TOOLS = (
    " When TestRail access is configured you also have tools: `get_testrail_case` to "
    "read any other case by ID, and `update_testrail_case` to write a title/Preconditions "
    "change directly to TestRail. Only call `update_testrail_case` when the user has "
    "explicitly asked you to save, apply, or publish a change; never write proactively."
)
```

with:

```python
_CHAT_SYSTEM_PROMPT_TOOLS = (
    " You have tools available covering: reading and looking up TestRail cases and "
    "Easy BDD test files, validating and running tests, inspecting failure traces and "
    "previewing/applying fixes, crawling a device to generate tests, generating or "
    "improving test cases with Ollama, and writing/pushing cases to TestRail. Only "
    "perform a real write, run, push, or crawl when the user has explicitly asked you "
    "to save, apply, run, or publish something; never do so proactively. Prefer "
    "read-only or preview/dry-run tools first when you're unsure."
)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `env/bin/python -m pytest tests/unit/test_builder_chat_system_prompt.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add frontend/builder_chat.py tests/unit/test_builder_chat_system_prompt.py
git commit -m "docs: generalize builder chat system prompt tool description"
```

---

### Task 6: Full regression pass and manual smoke test

**Files:** none (verification only)

- [ ] **Step 1: Run the full unit test suite**

Run: `env/bin/python -m pytest tests/unit -v`
Expected: all tests PASS, including every test added in Tasks 1-5.

- [ ] **Step 2: Manual smoke test — local builder (9093)**

```bash
env/bin/python frontend/start_local_builder.py
```

In a browser, open `http://localhost:9093`, use the chat box to ask
something only an MCP tool can answer (e.g. "what tests exist under
tests/cases?"). Confirm the reply reflects real file contents, not a
hallucinated answer — proves `list_tests` was actually called through
`run_mcp_tool`.

- [ ] **Step 3: Manual smoke test — TestRail builder (8091)**

```bash
env/bin/python frontend/start_testrail_builder.py
```

In a browser, open `http://localhost:8091`, repeat the same chat prompt as
Step 2, and additionally confirm the original two tools still work (ask it
to look up a known TestRail case by ID).

- [ ] **Step 4: Confirm write-gating instruction holds**

In either builder's chat, phrase a prompt that could trigger a real
mutation without explicitly asking for it (e.g. describe a test and ask
"does this look right?" rather than "run this"). Confirm the assistant
does not call `apply_fix`/`run_tests`/`repush_yaml_to_testrail` unprompted.
This is a judgment call on the model's part per the system prompt from
Task 5, not something the test suite enforces — record the observed
behavior in the PR description.
