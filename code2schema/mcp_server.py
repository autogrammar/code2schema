"""code2schema MCP server — dependency-free stdio JSON-RPC.

Adopts wellmanifest/poa (typed tools, closed inputSchema, fail-closed
dispatch) and wellmanifest/logs (append-only hash-chained JSONL event
stream under $XDG_STATE_HOME/code2schema/mcp-events.jsonl, overridable
with CODE2SCHEMA_MCP_EVENT_LOG).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Callable

_PROTOCOL_VERSION = "2024-11-05"
_NOTIFICATIONS = frozenset({"notifications/initialized", "notifications/cancelled"})

SERVER_NAME = "code2schema"
try:
    from importlib.metadata import version as _pkg_version

    SERVER_VERSION = _pkg_version("code2schema")
except Exception:
    SERVER_VERSION = "0.0.0"

_ZERO_HASH = "0" * 64


def _event_log_path() -> Path:
    override = os.environ.get("CODE2SCHEMA_MCP_EVENT_LOG")
    if override:
        return Path(override)
    state_home = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return state_home / "code2schema" / "mcp-events.jsonl"


def _emit_event(tool: str, status: str, duration_ms: int, detail: str = "") -> None:
    """Append one hash-chained event; logging failure never breaks a tool call."""
    try:
        path = _event_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        prev = _ZERO_HASH
        if path.exists() and path.stat().st_size:
            with path.open("rb") as fh:
                fh.seek(0, os.SEEK_END)
                tail = fh.read(65536).decode("utf-8", errors="replace")
            last = tail.rstrip().rsplit("\n", 1)[-1]
            prev = json.loads(last).get("event_hash", _ZERO_HASH)
        event = {
            "schema": "code2schema.mcp/event/v1",
            "event_id": f"event:{uuid.uuid4().hex[:24]}",
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "actor": "agent:mcp",
            "tool": tool,
            "status": status,
            "duration_ms": duration_ms,
            "detail": detail[:200],
            "prev_hash": prev,
        }
        body = json.dumps(event, sort_keys=True)
        event["event_hash"] = hashlib.sha256(body.encode()).hexdigest()
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event) + "\n")
    except Exception:
        pass


def _load_graph(path: str, exclude: list[str] | None):
    from code2schema.analyzer.cqrs import analyze
    from code2schema.analyzer.graph import build_rich_graph
    from code2schema.core.extractor import extract_project

    root = Path(path)
    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    modules = extract_project(root, exclude=exclude or None)
    if not modules:
        raise ValueError(f"No .py files found under: {path}")
    schema = analyze(modules)
    return modules, schema, build_rich_graph(schema)


def _tool_analyze(args: dict[str, Any]) -> str:
    from code2schema.codegen import to_json

    _, schema, _ = _load_graph(args["path"], args.get("exclude"))
    return to_json(schema)


def _tool_summary(args: dict[str, Any]) -> str:
    from code2schema.analyzer.events import infer_event_model
    from code2schema.analyzer.graph import detect_cycles, graph_summary

    modules, schema, G = _load_graph(args["path"], args.get("exclude"))
    cycles = detect_cycles(G)
    result = {
        "modules": len(modules),
        "functions": len(schema.all_functions()),
        "queries": len(schema.queries()),
        "commands": len(schema.commands()),
        "orchestrators": len(schema.orchestrators()),
        "workflows": len(schema.workflows),
        "rules": len(schema.rules),
        "graph_nodes": G.number_of_nodes(),
        "graph_edges": G.number_of_edges(),
        "cycles": len(cycles),
        "graph_summary": graph_summary(G, schema),
        "event_model": infer_event_model(modules).summary(),
    }
    return json.dumps(result, indent=2, default=str)


def _tool_cycles(args: dict[str, Any]) -> str:
    from code2schema.analyzer.graph import detect_cycles

    _, _, G = _load_graph(args["path"], args.get("exclude"))
    return json.dumps({"cycles": detect_cycles(G)}, indent=2)


def _tool_proto(args: dict[str, Any]) -> str:
    from code2schema.codegen import to_proto

    _, schema, _ = _load_graph(args["path"], args.get("exclude"))
    return to_proto(schema)


_PATH_PROPERTIES = {
    "path": {"type": "string", "description": "Project directory to analyze"},
    "exclude": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Directory/file names to exclude",
    },
}

TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "code2schema_analyze": {
        "name": "code2schema_analyze",
        "description": "Compile a Python project to the full CQRS SchemaIR JSON (commands, queries, workflows, rules).",
        "inputSchema": {
            "type": "object",
            "properties": _PATH_PROPERTIES,
            "required": ["path"],
        },
    },
    "code2schema_summary": {
        "name": "code2schema_summary",
        "description": "Compact analysis summary: module/function/command counts, graph size, cycles, event model.",
        "inputSchema": {
            "type": "object",
            "properties": _PATH_PROPERTIES,
            "required": ["path"],
        },
    },
    "code2schema_cycles": {
        "name": "code2schema_cycles",
        "description": "Detect dependency cycles in the CQRS graph.",
        "inputSchema": {
            "type": "object",
            "properties": _PATH_PROPERTIES,
            "required": ["path"],
        },
    },
    "code2schema_proto": {
        "name": "code2schema_proto",
        "description": "Generate proto3 definition from the CQRS schema.",
        "inputSchema": {
            "type": "object",
            "properties": _PATH_PROPERTIES,
            "required": ["path"],
        },
    },
}

TOOL_HANDLERS: dict[str, Callable[[dict[str, Any]], str]] = {
    "code2schema_analyze": _tool_analyze,
    "code2schema_summary": _tool_summary,
    "code2schema_cycles": _tool_cycles,
    "code2schema_proto": _tool_proto,
}


def _handle_initialize(request_id: Any, params: dict[str, Any] | None) -> dict[str, Any]:
    client_version = (params or {}).get("protocolVersion", _PROTOCOL_VERSION)
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": client_version,
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "capabilities": {"tools": {}},
        },
    }


def _handle_tools_list(request_id: Any) -> dict[str, Any]:
    tools = [
        {
            "name": schema["name"],
            "description": schema["description"],
            "inputSchema": schema["inputSchema"],
        }
        for schema in TOOL_SCHEMAS.values()
    ]
    return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}


def _handle_tools_call(request_id: Any, params: dict[str, Any]) -> dict[str, Any]:
    tool_name = params.get("name")
    arguments = params.get("arguments", {}) or {}

    if tool_name not in TOOL_HANDLERS:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"},
        }

    start = time.monotonic()
    try:
        result = TOOL_HANDLERS[tool_name](arguments)
        _emit_event(tool_name, "ok", int((time.monotonic() - start) * 1000))
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"content": [{"type": "text", "text": result}]},
        }
    except Exception as exc:
        _emit_event(
            tool_name, "error", int((time.monotonic() - start) * 1000), str(exc)
        )
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": f"Tool execution failed: {exc}"},
        }


def handle_request(request: dict[str, Any]) -> dict[str, Any]:
    method = request.get("method", "")
    params = request.get("params", {}) or {}
    request_id = request.get("id")

    if method in _NOTIFICATIONS:
        return {}
    if method == "initialize":
        return _handle_initialize(request_id, params)
    if method == "tools/list":
        return _handle_tools_list(request_id)
    if method == "tools/call":
        return _handle_tools_call(request_id, params)

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"Method '{method}' not found"},
    }


def run_server() -> None:
    print("code2schema MCP Server started", file=sys.stderr)
    print(f"Available tools: {', '.join(sorted(TOOL_SCHEMAS))}", file=sys.stderr)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            if response:
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError as exc:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": f"Parse error: {exc}"},
                    }
                ),
                flush=True,
            )
        except Exception as exc:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": f"Internal error: {exc}"},
                    }
                ),
                flush=True,
            )


def main() -> None:
    run_server()


if __name__ == "__main__":
    main()
