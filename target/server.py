import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from target.handlers import RouteHandler

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8080


class _CalculatorHTTPServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        route_handler: RouteHandler | None = None,
    ) -> None:
        self.route_handler = route_handler or RouteHandler()
        super().__init__(server_address, _CalculatorHTTPRequestHandler)


class _CalculatorHTTPRequestHandler(BaseHTTPRequestHandler):
    server: _CalculatorHTTPServer  # type: ignore[assignment]

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/calculate":
            self._send_json(404, {"error": "not found"})
            return
        try:
            payload = self.server.route_handler.handle_calculate(parsed.query)
            self._send_json(200, payload)
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
        except ZeroDivisionError:
            self._send_json(400, {"error": "division by zero"})

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        """Suppress default stderr access logging (zero observability)."""


def create_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    route_handler: RouteHandler | None = None,
) -> _CalculatorHTTPServer:
    return _CalculatorHTTPServer((host, port), route_handler=route_handler)


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    server = create_server(host, port)
    server.serve_forever()


if __name__ == "__main__":
    run_server()
