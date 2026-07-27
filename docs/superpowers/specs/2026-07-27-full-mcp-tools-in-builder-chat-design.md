# Expose all Easy BDD MCP tools in the builder chat assistants

Date: 2026-07-27

## Problem

`frontend/testrail_builder.py` (port 8091) and `frontend/local_builder.py`
(port 9093) each embed an Ollama/GitHub-Models chat assistant
(`frontend/builder_chat.py`) that today can only call two hand-written
tools: `get_testrail_case` and `update_testrail_case`. The full Easy BDD
toolset — `list_tests`, `run_tests`, `apply_fix`, `crawl_device`,
`ollama_generate_tests`, `repush_yaml_to_testrail`, etc. (20 tools total,
defined as `@mcp.tool()` functions in `easybdd/mcp_server.py`) — is only
reachable through an actual MCP client (Claude Code, Claude Desktop), not
from inside either builder's own chat box.

Goal: make all 20 MCP tools callable from both builders' chat assistants,
without hand-writing 20 duplicate tool schemas or duplicating tool logic.

## Decisions made during brainstorming

1. **Scope**: both builders (8091 and 9093) get the full tool set, via the
   shared `builder_chat.py`/`builder_core.py` code both already import from.
2. **Write safety**: trust-the-model. Same posture as today's
   `update_testrail_case` — tool descriptions instruct the model to only
   perform real writes/runs when the user has explicitly asked for it. No
   new code-level confirmation gate. Existing per-tool safety already in
   `mcp_server.py` (e.g. `run_tests` defaults `dry_run=True`, `apply_fix`
   requires `confirmed=True`) is unchanged and still applies, since the
   bridge calls the real functions.
3. **Schema generation**: auto-generate tool schemas and dispatch from
   `easybdd.mcp_server`'s existing `FastMCP` instance, rather than
   hand-writing 20 schema blocks. New MCP tools added later appear in the
   chat automatically with no edits to the builder apps.

## Architecture

### New module: `frontend/mcp_tool_bridge.py`

Imports the already-constructed `mcp = FastMCP(...)` object directly from
`easybdd.mcp_server` (confirmed: importing that module has no side effects —
the STDIO/SSE server only starts when `serve()` is called explicitly from
the CLI entrypoint, which the builder apps never call).

```python
from easybdd.mcp_server import mcp

async def list_mcp_tool_defs() -> list[dict]:
    """OpenAI/Ollama-style tool schemas for every registered MCP tool."""
    tools = await mcp.list_tools()
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": t.inputSchema,
            },
        }
        for t in tools
    ]

async def run_mcp_tool(name: str, args: dict) -> str:
    """Invoke an MCP tool by name and return a JSON-string-safe result."""
    result = await mcp.call_tool(name, args)
    return _stringify(result)
```

`_stringify` normalizes whatever `call_tool` returns (a list of MCP content
blocks, most commonly `TextContent` items, or occasionally a plain dict) into
a single string: join `.text` from content blocks, or `json.dumps` a dict.

`list_mcp_tool_defs()`'s result is computed once per process (module-level
cache) — the registered tool set doesn't change at runtime.

### Wiring into `testrail_builder.py` and `local_builder.py`

Each app already builds its own hand-written `TESTRAIL_CHAT_TOOLS` /
`_run_chat_tool` (or local-builder equivalent) for its two app-specific
tools. Each app now also computes `await list_mcp_tool_defs()` once at
startup and concatenates it onto its hand-written tool list before passing
to `register_chat_routes`.

Dispatch becomes a combined async function per app:

```python
async def _run_chat_tool(name: str, args: dict) -> str:
    if name in {"get_testrail_case", "update_testrail_case"}:
        return _run_local_tool(name, args)   # existing hand-written logic, unchanged
    return await run_mcp_tool(name, args)
```

No name collisions exist between the two hand-written tools and the 20 MCP
tool names (verified against `easybdd/mcp_server.py`).

### `builder_chat.py` change (shared by both apps)

`register_chat_routes`'s tool-call loop currently calls the runner
synchronously:

```python
output = tool_runner(name, args) if tool_runner else json.dumps(...)
```

Since MCP tools include at least one `async def` (`crawl_device`), and the
new combined dispatcher above is itself `async def`, this call must support
awaiting. Change to:

```python
output = tool_runner(name, args) if tool_runner else json.dumps(...)
if inspect.isawaitable(output):
    output = await output
```

This is backward compatible: the existing synchronous `get_testrail_case`/
`update_testrail_case` closures keep working unchanged (a plain `str` is not
awaitable, so the `await` branch is skipped for them).

### System prompt

`_CHAT_SYSTEM_PROMPT_TOOLS` currently hand-lists the two TestRail tools by
name. Replace with a generic paragraph describing the tool categories
available (test discovery/validation/running, failure-trace + fix preview,
device crawling, Ollama-assisted case generation, TestRail read/write) and
the same standing instruction: only perform real writes, runs, or pushes
when the user has explicitly asked for it. This avoids hand-maintaining a
name list that drifts as `mcp_server.py`'s tool set changes, while keeping
the "don't act without being asked" rule prominent for both hand-written and
MCP-backed tools.

## Out of scope

- No new confirmation-token / two-step-approval flow (declined during
  brainstorming in favor of trust-the-model).
- No change to `easybdd/mcp_server.py` itself — the bridge only reads its
  already-registered tools.
- No dedup/merge of the two hand-written tools into the MCP tool set; they
  stay as-is since they aren't defined there.

## Testing

- Unit-level: `mcp_tool_bridge.list_mcp_tool_defs()` returns 20 schemas with
  non-empty `name`/`parameters` for each.
- Manual: from each builder's chat box, prompt something that requires an
  MCP-only tool (e.g. "list the tests in tests/cases") and confirm a real
  tool call round-trips and the model uses the result in its reply.
- Manual: confirm a write-shaped prompt (e.g. "run this test for real") only
  fires when explicitly asked, per the updated system prompt.
