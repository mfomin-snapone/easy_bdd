from __future__ import annotations

import inspect
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from builder_core import CATALOG

ROOT = Path(__file__).resolve().parent.parent

GITHUB_MODELS_BASE_URL = "https://models.github.ai"
GITHUB_API_VERSION = "2026-03-10"
GITHUB_CATALOG_CACHE_TTL_SECONDS = 300
MAX_CHAT_TOOL_ROUNDS = 4
MAX_CASE_CONTEXT_ISSUES = 8
MAX_CASE_CONTEXT_BODY_CHARS = 3000

_GITHUB_CATALOG_CACHE: Dict[str, Dict[str, Any]] = {}


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCaseContext(BaseModel):
    """The case currently open in the builder editor, sent with every chat
    turn so the assistant doesn't need the user to paste a case ID it can
    already see on screen."""

    case_id: Optional[int | str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    case_context: Optional[ChatCaseContext] = None
    provider: str = "ollama"
    github_token: Optional[str] = None
    github_model: Optional[str] = None


class ChatStatusRequest(BaseModel):
    provider: str = "ollama"
    github_token: Optional[str] = None
    github_model: Optional[str] = None


class ChatModelsRequest(BaseModel):
    provider: str = "ollama"
    github_token: Optional[str] = None
    github_model: Optional[str] = None


def _load_framework_doc() -> str:
    sections = (
        "1. Case Naming",
        "2. Var: Cases",
        "3. Preconditions Field Format",
        "6. Assertions",
        "10. Selector Strategies",
    )
    try:
        text = (ROOT / "docs" / "writing-test-cases.md").read_text(encoding="utf-8")
    except OSError:
        return ""
    kept = [
        "## " + section
        for section in text.split("\n## ")[1:]
        if section.startswith(sections)
    ]
    return "\n\n".join(kept).strip()


def _action_reference_markdown() -> str:
    by_category: Dict[str, List[str]] = {}
    for action_id, definition in sorted(CATALOG.items()):
        params = definition.get("parameters") or {}
        required = [name for name, cfg in params.items() if cfg.get("required")]
        entry = f"- `{action_id}`"
        if required:
            entry += f" (required: {', '.join(required)})"
        by_category.setdefault(definition.get("category", "Other"), []).append(entry)

    lines: List[str] = []
    for category in sorted(by_category):
        lines.append(f"### {category}")
        lines.extend(by_category[category])
    return "\n".join(lines)


_FRAMEWORK_DOC_REF = _load_framework_doc()
_ACTION_REF = _action_reference_markdown()

_CHAT_SYSTEM_PROMPT_BASE = (
    "You are the AI assistant embedded in the Easy BDD test builder. "
    "You help the user author BDD-style test cases (Var:, Shared:, Setup:, "
    "Teardown:, Feature:), pick the right builder actions, and troubleshoot the "
    "Preconditions YAML the app generates. Use framework reference and action "
    "list when provided as ground truth; do not invent actions or syntax that are not in them.\n\n"
    "If the user has a case open in the builder, its title, Preconditions YAML, and "
    "current validation errors/warnings are provided in a separate 'Currently open "
    "test case' message on every turn; treat that as ground truth about what they are "
    "looking at, and do not ask them to paste a case ID that is already given there."
)


_CHAT_AUTHORING_RULES = (
    "\n\nAuthoring rules for this builder:\n"
    "- When the user asks you to create or refine a test case, default to returning builder-ready Easy BDD output, not generic testing advice.\n"
    "- Prefer this response structure when drafting: Suggested Case Title, then Preconditions YAML, then 1-3 short next questions or assumptions.\n"
    "- Preconditions YAML for this builder must use the flush-left Easy BDD format: after `- action:`, put params on following lines with no extra indentation.\n"
    "- Do not output normally indented YAML under an action unless the user explicitly asks for generic YAML.\n"
    "- Add `# N. description` comment lines before steps when drafting a case.\n"
    "- Prefer framework-native assertion actions such as `test.assert_element_visible`, `test.assert_text_contains`, `test.assert_text_equals`, and `test.assert` when they fit better than vague browser checks.\n"
    "- Prefer stable selectors and user-facing locators. Use role/name, label, or durable selectors when known; avoid brittle selectors when you can.\n"
    "- If required inputs are missing, ask the smallest useful follow-up question instead of inventing specifics.\n"
    "- If the user is clearly brainstorming rather than asking for a ready draft, stay concise and ask a focused clarifying question."
)


_CHAT_GUIDED_WORKFLOW = (
    "\n\nGuided workflow expectations:\n"
    "- Behave like a guided test-authoring assistant inside the builder, not just a chatbot.\n"
    "- For browser/UI tests, lead the user step by step: page entry point, critical assertions, interaction steps, expected results, then cleanup if needed.\n"
    "- When selectors or page details are uncertain, ask for one concrete artifact next: a pasted recording, the visible labels/button text, or the exact element attributes.\n"
    "- If the user mentions a login page, landing page, wizard, form, or settings screen, propose the smallest sensible first case before expanding into a full suite.\n"
    "- Keep momentum: after drafting a case, immediately suggest the next missing detail to make it executable in this builder."
)


_CHAT_BROWSER_CAPABILITY_NOTE = (
    "\n\nBrowser assistance boundaries:\n"
    "- You can guide browser test authoring, interpret pasted recordings, and refine the currently open case.\n"
    "- Do not claim that you can directly click or inspect the live browser from this chat unless the user has provided a recording or explicit page details through the builder workflow.\n"
    "- If live UI details are needed, tell the user exactly what to provide next in the builder context."
)


_CHAT_SYSTEM_PROMPT_TOOLS = (
    " When TestRail access is configured you also have tools: `get_testrail_case` to "
    "read any other case by ID, and `update_testrail_case` to write a title/Preconditions "
    "change directly to TestRail. Only call `update_testrail_case` when the user has "
    "explicitly asked you to save, apply, or publish a change; never write proactively."
)


def _chat_system_prompt(provider: str, include_tools: bool) -> str:
    speed_note = (
        " This Ollama model runs locally on a CPU-only host, so keep answers short "
        "(a few sentences or a short snippet); long answers take a long time to generate."
        if provider == "ollama"
        else " Keep answers focused and concise unless the user explicitly asks for a detailed draft."
    )
    tool_note = _CHAT_SYSTEM_PROMPT_TOOLS if include_tools else ""
    return (
        _CHAT_SYSTEM_PROMPT_BASE
        + speed_note
        + _CHAT_AUTHORING_RULES
        + _CHAT_GUIDED_WORKFLOW
        + _CHAT_BROWSER_CAPABILITY_NOTE
        + "\n\n"
        + tool_note.strip()
    )


def _chat_system_prompt_full(provider: str, include_tools: bool) -> str:
    return (
        _chat_system_prompt(provider, include_tools)
        + "\n\n# Framework syntax reference\n\n"
        + _FRAMEWORK_DOC_REF
        + "\n\n# Available builder actions (id and required params)\n\n"
        + _ACTION_REF
    )


def _chat_system_prompt_light(provider: str, include_tools: bool) -> str:
    return (
        _chat_system_prompt(provider, include_tools)
        + "\n\nPerformance mode for early turns: if the request is underspecified, ask one focused "
          "clarifying question first. Avoid large YAML blocks until requirements are clear."
    )


def _chat_num_ctx() -> int:
    return int(os.getenv("BUILDER_CHAT_NUM_CTX", "8192"))


def _chat_max_tokens() -> int:
    return int(os.getenv("BUILDER_CHAT_MAX_TOKENS", "350"))


def _chat_keep_alive() -> str:
    return os.getenv("BUILDER_CHAT_KEEP_ALIVE", "30m")


def _chat_lightweight_first_turn_enabled() -> bool:
    raw = os.getenv("BUILDER_CHAT_LIGHTWEIGHT_FIRST_TURN", "true").strip().lower()
    return raw in ("1", "true", "yes", "on")


def _ollama_base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")


def _ollama_chat_model() -> str:
    return os.getenv("BUILDER_CHAT_MODEL", "qwen2.5-coder:7b")


def _github_token(requested_token: Optional[str]) -> Optional[str]:
    token = (requested_token or "").strip()
    if token:
        return token
    env_token = os.getenv("GITHUB_TOKEN", "").strip()
    return env_token or None


def _normalize_github_model_id(model: str) -> str:
    normalized = (model or "").strip()
    if not normalized:
        return normalized
    if "/" in normalized:
        return normalized
    openai_prefixes = ("gpt-", "o1", "o3", "o4", "text-embedding-")
    if normalized.startswith(openai_prefixes):
        return f"openai/{normalized}"
    return normalized


def _github_chat_model(requested_model: Optional[str]) -> str:
    raw = requested_model or os.getenv("BUILDER_GITHUB_CHAT_MODEL", "openai/gpt-5-chat")
    return _normalize_github_model_id(raw)


def _provider_name(raw: Optional[str]) -> str:
    provider = (raw or "ollama").strip().lower()
    if provider not in {"ollama", "github"}:
        raise HTTPException(status_code=422, detail=f"Unknown chat provider '{provider}'.")
    return provider


def _latest_user_text(messages: List[ChatMessage]) -> str:
    for msg in reversed(messages or []):
        if (msg.role or "").strip().lower() == "user":
            return (msg.content or "").strip()
    return ""


def _looks_detailed_request(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    lower = t.lower()
    hints = (
        "feature:", "shared:", "var:", "setup:", "teardown:", "steps:",
        "selector:", "store_as:", "test.assert", "preconditions",
        "- browser.", "- api.", "- websocket.", "- telnet.", "- ssh.",
    )
    if sum(1 for hint in hints if hint in lower) >= 2:
        return True
    if len(lower.split()) >= 45:
        return True
    if len([line for line in t.splitlines() if line.strip()]) >= 5:
        return True
    return False


def _use_full_prompt_context(req: ChatRequest) -> bool:
    if not _chat_lightweight_first_turn_enabled():
        return True

    ctx = req.case_context
    if ctx and (ctx.case_id or ctx.body or ctx.errors or ctx.warnings):
        return True
    if len(req.messages or []) > 1:
        return True
    return _looks_detailed_request(_latest_user_text(req.messages))


def _case_context_message(ctx: Optional[ChatCaseContext]) -> Optional[Dict[str, Any]]:
    if not ctx or not (ctx.case_id or ctx.title or ctx.body):
        return None
    lines = [
        "# Currently open test case in the builder",
        "(unpublished edits - may not match the persisted version yet)",
    ]
    if ctx.case_id:
        lines.append(f"Case ID: {ctx.case_id}")
    if ctx.title:
        lines.append(f"Title: {ctx.title}")
    if ctx.errors:
        shown = ctx.errors[:MAX_CASE_CONTEXT_ISSUES]
        suffix = f"\n- ...and {len(ctx.errors) - len(shown)} more" if len(ctx.errors) > len(shown) else ""
        lines.append("Validation errors:\n" + "\n".join(f"- {err}" for err in shown) + suffix)
    if ctx.warnings:
        shown = ctx.warnings[:MAX_CASE_CONTEXT_ISSUES]
        suffix = f"\n- ...and {len(ctx.warnings) - len(shown)} more" if len(ctx.warnings) > len(shown) else ""
        lines.append("Validation warnings:\n" + "\n".join(f"- {warn}" for warn in shown) + suffix)
    if ctx.body:
        body = ctx.body
        if len(body) > MAX_CASE_CONTEXT_BODY_CHARS:
            body = body[:MAX_CASE_CONTEXT_BODY_CHARS] + f"\n... (truncated, {len(ctx.body)} chars total)"
        lines.append("Current Preconditions YAML:\n```yaml\n" + body + "\n```")
    return {"role": "system", "content": "\n\n".join(lines)}


def _parse_pseudo_tool_call(content: str, tool_names: set[str]) -> Optional[tuple[str, Dict[str, Any]]]:
    text = (content or "").strip()
    if not text:
        return None
    if text.startswith("```"):
        text = text.strip("`")
        if "\n" in text:
            text = text.split("\n", 1)[1]
    try:
        obj = json.loads(text)
    except ValueError:
        return None
    if not isinstance(obj, dict):
        return None
    name = obj.get("name")
    if name not in tool_names:
        return None
    args = obj.get("arguments") or {}
    if not isinstance(args, dict):
        return None
    return name, args


def _github_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }


def _http_error_detail(exc: httpx.HTTPError) -> str:
    response = getattr(exc, "response", None)
    if response is None:
        return str(exc)
    try:
        data = response.json()
    except ValueError:
        data = response.text or str(exc)
    if isinstance(data, dict):
        return data.get("message") or data.get("error") or json.dumps(data)
    return str(data)


def _http_error_status(exc: httpx.HTTPError, default: int = 502) -> int:
    response = getattr(exc, "response", None)
    if response is None:
        return default
    return int(getattr(response, "status_code", default) or default)


def _github_catalog_cache_key(token: Optional[str]) -> str:
    return (token or "").strip()


def _get_cached_github_catalog(token: Optional[str]) -> Optional[List[Dict[str, Any]]]:
    key = _github_catalog_cache_key(token)
    if not key:
        return None
    cached = _GITHUB_CATALOG_CACHE.get(key)
    if not cached:
        return None
    if (time.time() - float(cached.get("ts", 0))) > GITHUB_CATALOG_CACHE_TTL_SECONDS:
        _GITHUB_CATALOG_CACHE.pop(key, None)
        return None
    models = cached.get("models")
    return models if isinstance(models, list) else None


def _set_cached_github_catalog(token: Optional[str], models: List[Dict[str, Any]]) -> None:
    key = _github_catalog_cache_key(token)
    if not key:
        return
    _GITHUB_CATALOG_CACHE[key] = {"ts": time.time(), "models": models}


async def _fetch_github_catalog(token: str) -> List[Dict[str, Any]]:
    cached = _get_cached_github_catalog(token)
    if cached is not None:
        return cached
    async with httpx.AsyncClient(timeout=12) as client:
        resp = await client.get(
            f"{GITHUB_MODELS_BASE_URL}/catalog/models",
            headers=_github_headers(token),
        )
        resp.raise_for_status()
        data = resp.json()
    models = data if isinstance(data, list) else []
    _set_cached_github_catalog(token, models)
    return models


async def _fetch_ollama_tags() -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=8) as client:
        resp = await client.get(f"{_ollama_base_url()}/api/tags")
        resp.raise_for_status()
        data = resp.json()
    models = data.get("models") if isinstance(data, dict) else []
    return models if isinstance(models, list) else []


def _github_catalog_to_chat_models(items: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        model_id = str(item.get("id") or "").strip()
        if not model_id:
            continue
        outputs = {str(v).lower() for v in (item.get("supported_output_modalities") or [])}
        inputs = {str(v).lower() for v in (item.get("supported_input_modalities") or [])}
        if "text" not in outputs or "text" not in inputs:
            continue
        if "embedding" in model_id:
            continue
        results.append({"id": model_id, "label": model_id})
    results.sort(key=lambda item: item["id"])
    return results


def _ollama_tags_to_chat_models(items: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or item.get("model") or "").strip()
        if not name:
            continue
        results.append({"id": name, "label": name})
    results.sort(key=lambda item: item["id"])
    return results


async def _ollama_status() -> Dict[str, Any]:
    try:
        await _fetch_ollama_tags()
    except httpx.HTTPError:
        return {"configured": False, "provider": "ollama", "model": _ollama_chat_model()}
    except Exception:
        return {"configured": False, "provider": "ollama", "model": _ollama_chat_model()}
    return {"configured": True, "provider": "ollama", "model": _ollama_chat_model()}


async def _github_status(token: Optional[str], requested_model: Optional[str]) -> Dict[str, Any]:
    model = _github_chat_model(requested_model)
    token = _github_token(token)
    if not token:
        return {
            "configured": False,
            "provider": "github",
            "model": model,
            "message": "GitHub PAT required",
        }
    models = _get_cached_github_catalog(token)
    if models is None:
        return {
            "configured": True,
            "provider": "github",
            "model": model,
            "message": "GitHub token present. Model list will validate availability.",
        }
    available = {item.get("id") for item in models if isinstance(item, dict)}
    if model not in available:
        return {
            "configured": False,
            "provider": "github",
            "model": model,
            "message": "Token is valid, but the selected model is not available to this account.",
        }
    return {
        "configured": True,
        "provider": "github",
        "model": model,
        "message": "GitHub Models ready",
    }


async def _provider_status(provider: str, token: Optional[str], requested_model: Optional[str]) -> Dict[str, Any]:
    if provider == "github":
        return await _github_status(token, requested_model)
    return await _ollama_status()


async def _provider_models(provider: str, token: Optional[str], requested_model: Optional[str]) -> Dict[str, Any]:
    if provider == "github":
        token = _github_token(token)
        model = _github_chat_model(requested_model)
        if not token:
            return {
                "configured": False,
                "provider": "github",
                "selected_model": model,
                "models": [],
                "message": "GitHub PAT required",
            }
        try:
            models = _github_catalog_to_chat_models(await _fetch_github_catalog(token))
        except httpx.HTTPError as exc:
            return {
                "configured": False,
                "provider": "github",
                "selected_model": model,
                "models": [],
                "message": _http_error_detail(exc),
            }
        except Exception as exc:
            return {
                "configured": False,
                "provider": "github",
                "selected_model": model,
                "models": [],
                "message": str(exc),
            }
        if model and all(item["id"] != model for item in models):
            models.insert(0, {"id": model, "label": f"{model} (current)"})
        return {
            "configured": True,
            "provider": "github",
            "selected_model": model,
            "models": models,
        }

    selected = _ollama_chat_model()
    try:
        models = _ollama_tags_to_chat_models(await _fetch_ollama_tags())
    except httpx.HTTPError as exc:
        return {
            "configured": False,
            "provider": "ollama",
            "selected_model": selected,
            "models": [],
            "message": _http_error_detail(exc),
        }
    except Exception as exc:
        return {
            "configured": False,
            "provider": "ollama",
            "selected_model": selected,
            "models": [],
            "message": str(exc),
        }
    if selected and all(item["id"] != selected for item in models):
        models.insert(0, {"id": selected, "label": f"{selected} (configured)"})
    return {
        "configured": True,
        "provider": "ollama",
        "selected_model": selected,
        "models": models,
    }


async def _call_ollama(
    messages: List[Dict[str, Any]],
    include_tools: bool,
    tool_defs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "model": _ollama_chat_model(),
        "stream": False,
        "keep_alive": _chat_keep_alive(),
        "messages": messages,
        "options": {
            "num_ctx": _chat_num_ctx(),
            "num_predict": _chat_max_tokens(),
        },
    }
    if include_tools:
        payload["tools"] = tool_defs
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(f"{_ollama_base_url()}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="Ollama request timed out; the local model may be busy or the prompt is too large.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Ollama error: {_http_error_detail(exc)}") from exc
    return {"message": data.get("message", {}) or {}, "model": _ollama_chat_model()}


async def _call_github(
    messages: List[Dict[str, Any]],
    token: str,
    requested_model: Optional[str],
    include_tools: bool,
    tool_defs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "model": _github_chat_model(requested_model),
        "messages": messages,
        "stream": False,
        "max_tokens": _chat_max_tokens(),
        "temperature": 0.2,
    }
    if include_tools:
        payload["tools"] = tool_defs
        payload["tool_choice"] = "auto"
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{GITHUB_MODELS_BASE_URL}/inference/chat/completions",
                headers=_github_headers(token),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="GitHub Models request timed out.") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=_http_error_status(exc),
            detail=f"GitHub Models error: {_http_error_detail(exc)}",
        ) from exc
    try:
        message = (data.get("choices") or [])[0].get("message", {}) or {}
    except Exception as exc:
        raise HTTPException(status_code=502, detail="GitHub Models returned an unexpected response.") from exc
    return {"message": message, "model": _github_chat_model(requested_model)}


async def _call_provider(
    provider: str,
    messages: List[Dict[str, Any]],
    token: Optional[str],
    requested_model: Optional[str],
    include_tools: bool,
    tool_defs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    if provider == "github":
        token = _github_token(token)
        if not token:
            raise HTTPException(status_code=422, detail="GitHub PAT required for the GitHub provider.")
        return await _call_github(messages, token, requested_model, include_tools, tool_defs)
    return await _call_ollama(messages, include_tools, tool_defs)


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


def register_chat_routes(
    app: FastAPI,
    *,
    tool_defs: Optional[List[Dict[str, Any]]] = None,
    tool_runner: Optional[Callable[[str, Dict[str, Any]], Any]] = None,
    tools_available: Optional[Callable[[], bool]] = None,
) -> None:
    tool_defs = tool_defs or []
    tool_names = {t.get("function", {}).get("name") for t in tool_defs if isinstance(t, dict)}
    tool_names.discard(None)

    @app.get("/api/chat/status")
    async def chat_status_legacy():
        return await _ollama_status()

    @app.post("/api/chat/status")
    async def chat_status(req: ChatStatusRequest):
        provider = _provider_name(req.provider)
        return await _provider_status(provider, _github_token(req.github_token), req.github_model)

    @app.post("/api/chat/models")
    async def chat_models(req: ChatModelsRequest):
        provider = _provider_name(req.provider)
        return await _provider_models(provider, req.github_token, req.github_model)

    @app.post("/api/chat")
    async def chat(req: ChatRequest):
        provider = _provider_name(req.provider)
        include_tools = bool(tool_defs and tool_runner and (tools_available() if tools_available else True))
        system_prompt = (
            _chat_system_prompt_full(provider, include_tools)
            if _use_full_prompt_context(req)
            else _chat_system_prompt_light(provider, include_tools)
        )
        messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]
        case_msg = _case_context_message(req.case_context)
        if case_msg:
            messages.append(case_msg)
        messages += [{"role": msg.role, "content": msg.content} for msg in req.messages]

        for _ in range(MAX_CHAT_TOOL_ROUNDS):
            result = await _call_provider(
                provider,
                messages,
                _github_token(req.github_token),
                req.github_model,
                include_tools,
                tool_defs,
            )
            message = result["message"]
            tool_calls = list(message.get("tool_calls") or [])
            pseudo_call = None
            if provider == "ollama" and not tool_calls and include_tools and tool_names:
                pseudo_call = _parse_pseudo_tool_call(message.get("content", ""), tool_names)
            if not tool_calls and not pseudo_call:
                return {
                    "reply": message.get("content", ""),
                    "provider": provider,
                    "model": result["model"],
                }

            messages.append({
                "role": message.get("role", "assistant"),
                "content": message.get("content", ""),
                **({"tool_calls": tool_calls} if tool_calls else {}),
            })

            if pseudo_call:
                name, args = pseudo_call
                output = await _invoke_tool_runner(tool_runner, name, args)
                messages.append({"role": "tool", "content": output})
                continue

            for call in tool_calls:
                fn = call.get("function", {}) or {}
                name = fn.get("name", "")
                args = fn.get("arguments") or {}
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except ValueError:
                        args = {}
                output = await _invoke_tool_runner(tool_runner, name, args)
                tool_message = {"role": "tool", "content": output}
                if provider == "github":
                    if call.get("id"):
                        tool_message["tool_call_id"] = call["id"]
                    if name:
                        tool_message["name"] = name
                messages.append(tool_message)

        final_result = await _call_provider(
            provider,
            messages,
            _github_token(req.github_token),
            req.github_model,
            False,
            tool_defs,
        )
        return {
            "reply": final_result["message"].get("content", ""),
            "provider": provider,
            "model": final_result["model"],
        }