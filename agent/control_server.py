"""Minimal agent control HTTP server stub — full API in PR-09 (§5.11 R24)."""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from agent.installer import disable_tracing_on_current_thread


class _ControlHandler(BaseHTTPRequestHandler):
    server_version = "HyperProbeControl/0.1"

    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        self.send_response(501)
        self.end_headers()


class AgentControlServer:
    """Background control server thread — tracing disabled on startup (§5.11)."""

    def __init__(self, host: str = "127.0.0.1", port: int = 9090) -> None:
        self._host = host
        self._port = port
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        if self._server is not None:
            return int(self._server.server_address[1])
        return self._port

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
        self._server = HTTPServer((self._host, self._port), _ControlHandler)
        self._server.serve_forever()
