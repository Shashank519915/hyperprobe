"""Agent control HTTP server on :9090 — separate from target :8080 (§5.4)."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from agent.breakpoints import breakpoint_from_dict, breakpoint_to_dict
from agent.installer import disable_tracing_on_current_thread
from agent.registry import BreakpointRegistry

DEFAULT_CONTROL_HOST = "0.0.0.0"
DEFAULT_CONTROL_PORT = 9090
BREAKPOINTS_PATH = "/breakpoints"


class _ControlHTTPServer(ThreadingHTTPServer):
    """HTTPServer that carries the breakpoint registry for handlers."""

    def __init__(
        self,
        server_address: tuple[str, int],
        request_handler_class: type[BaseHTTPRequestHandler],
        registry: BreakpointRegistry,
    ) -> None:
        self.registry = registry
        super().__init__(server_address, request_handler_class)
        self.daemon_threads = True

    def process_request_thread(self, request, client_address) -> None:  # noqa: ANN001
        disable_tracing_on_current_thread()
        super().process_request_thread(request, client_address)


class _ControlHandler(BaseHTTPRequestHandler):
    server: _ControlHTTPServer

    server_version = "HyperProbeControl/0.1"

    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        if not self._is_breakpoints_path():
            self._send_json(404, {"error": "not found"})
            return
        try:
            payload = [
                breakpoint_to_dict(bp) for bp in self.server.registry.list_all()
            ]
            self._send_json(200, payload)
        except Exception as exc:
            self._send_json(500, {"error": str(exc)})

    def do_POST(self) -> None:
        if not self._is_breakpoints_path():
            self._send_json(404, {"error": "not found"})
            return
        try:
            raw = self._read_json_body()
            bp = breakpoint_from_dict(raw)
            self.server.registry.register(bp)
            self._send_json(201, breakpoint_to_dict(bp))
        except json.JSONDecodeError:
            self._send_json(400, {"error": "malformed JSON"})
        except (ValueError, KeyError, TypeError) as exc:
            self._send_json(400, {"error": str(exc)})
        except Exception as exc:
            self._send_json(500, {"error": str(exc)})

    def _is_breakpoints_path(self) -> bool:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        return path == BREAKPOINTS_PATH

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b""
        if not body:
            raise json.JSONDecodeError("empty body", "", 0)
        payload = json.loads(body.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("body must be a JSON object")
        return payload

    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class AgentControlServer:
    """Background control API server — tracing disabled on startup (§5.11)."""

    def __init__(
        self,
        registry: BreakpointRegistry,
        *,
        host: str = DEFAULT_CONTROL_HOST,
        port: int = DEFAULT_CONTROL_PORT,
    ) -> None:
        self._registry = registry
        self._host = host
        self._port = port
        self._server: _ControlHTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        if self._server is not None:
            return int(self._server.server_address[1])
        return self._port

    @property
    def registry(self) -> BreakpointRegistry:
        return self._registry

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._thread = threading.Thread(
            target=self._serve,
            name="AgentControlServer",
            daemon=True,
        )
        self._thread.start()

    def stop(self, timeout: float | None = 5.0) -> None:
        if self._server is not None:
            self._server.shutdown()
        if self._thread is not None:
            self._thread.join(timeout)

    def _serve(self) -> None:
        disable_tracing_on_current_thread()
        self._server = _ControlHTTPServer(
            (self._host, self._port),
            _ControlHandler,
            self._registry,
        )
        self._server.serve_forever()
