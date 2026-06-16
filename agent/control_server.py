"""Agent control HTTP server on :9090 — separate from target :8080 (§5.4)."""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

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


class _ControlHandler(BaseHTTPRequestHandler):
    server: _ControlHTTPServer

    server_version = "HyperProbeControl/0.1"

    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        if self._is_breakpoints_path():
            self.send_response(501)
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:
        if self._is_breakpoints_path():
            self.send_response(501)
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

    def _is_breakpoints_path(self) -> bool:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        return path == BREAKPOINTS_PATH


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
