import json
import socket
import time
import urllib.error
import urllib.request

from agent.control_server import (
    BREAKPOINTS_PATH,
    DEFAULT_CONTROL_PORT,
    AgentControlServer,
)
from agent.registry import BreakpointRegistry


def _wait_for_server(server: AgentControlServer, timeout: float = 2.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline and server._server is None:  # noqa: SLF001
        time.sleep(0.01)
    assert server._server is not None  # noqa: SLF001


def _base_url(server: AgentControlServer) -> str:
    return f"http://127.0.0.1:{server.port}{BREAKPOINTS_PATH}"


def _get_json(url: str) -> tuple[int, object]:
    with urllib.request.urlopen(url, timeout=1.0) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def _post_json(url: str, payload: object) -> tuple[int, object]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=1.0) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def _post_raw(url: str, body: bytes) -> int:
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=1.0) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code


def test_default_control_port_is_9090():
    assert DEFAULT_CONTROL_PORT == 9090
    assert BREAKPOINTS_PATH == "/breakpoints"


def test_control_server_binds_ephemeral_port():
    registry = BreakpointRegistry()
    server = AgentControlServer(registry, host="127.0.0.1", port=0)
    server.start()
    try:
        _wait_for_server(server)
        assert server.port != 0
        with socket.create_connection(("127.0.0.1", server.port), timeout=1.0):
            pass
    finally:
        server.stop()


def test_get_breakpoints_returns_empty_list():
    registry = BreakpointRegistry()
    server = AgentControlServer(registry, host="127.0.0.1", port=0)
    server.start()
    try:
        _wait_for_server(server)
        status, payload = _get_json(_base_url(server))
        assert status == 200
        assert payload == []
    finally:
        server.stop()


def test_post_function_breakpoint_returns_201():
    registry = BreakpointRegistry()
    server = AgentControlServer(registry, host="127.0.0.1", port=0)
    server.start()
    try:
        _wait_for_server(server)
        status, payload = _post_json(
            _base_url(server),
            {"type": "function", "value": "add", "capture_mode": "ENTRY"},
        )
        assert status == 201
        assert payload["type"] == "function"
        assert payload["value"] == "add"
        assert payload["capture_mode"] == "ENTRY"
        assert "id" in payload
        assert len(registry.list_all()) == 1
    finally:
        server.stop()


def test_post_method_and_file_line_breakpoints():
    registry = BreakpointRegistry()
    server = AgentControlServer(registry, host="127.0.0.1", port=0)
    server.start()
    try:
        _wait_for_server(server)
        _, method_bp = _post_json(
            _base_url(server),
            {
                "type": "method",
                "value": "AdditionEngine.add",
                "capture_mode": "BOTH",
            },
        )
        _, line_bp = _post_json(
            _base_url(server),
            {
                "type": "file_line",
                "file": "target/engines/addition.py",
                "line": 5,
                "capture_mode": "RETURN",
            },
        )
        assert method_bp["type"] == "method"
        assert line_bp["file"] == "target/engines/addition.py"
        assert line_bp["line"] == 5
    finally:
        server.stop()


def test_post_upserts_existing_id():
    registry = BreakpointRegistry()
    server = AgentControlServer(registry, host="127.0.0.1", port=0)
    server.start()
    try:
        _wait_for_server(server)
        _, first = _post_json(
            _base_url(server),
            {"id": "bp-1", "type": "function", "value": "add"},
        )
        _, second = _post_json(
            _base_url(server),
            {
                "id": "bp-1",
                "type": "function",
                "value": "compute",
                "capture_mode": "RETURN",
            },
        )
        assert first["id"] == "bp-1"
        assert second["id"] == "bp-1"
        assert second["value"] == "compute"
        assert second["capture_mode"] == "RETURN"
        assert len(registry.list_all()) == 1
    finally:
        server.stop()


def test_get_breakpoints_lists_registered_items():
    registry = BreakpointRegistry()
    server = AgentControlServer(registry, host="127.0.0.1", port=0)
    server.start()
    try:
        _wait_for_server(server)
        _post_json(
            _base_url(server),
            {"id": "bp-a", "type": "function", "value": "add"},
        )
        status, payload = _get_json(_base_url(server))
        assert status == 200
        assert len(payload) == 1
        assert payload[0]["id"] == "bp-a"
    finally:
        server.stop()


def test_post_missing_required_fields_returns_400():
    registry = BreakpointRegistry()
    server = AgentControlServer(registry, host="127.0.0.1", port=0)
    server.start()
    try:
        _wait_for_server(server)
        url = _base_url(server)
        with urllib.request.urlopen(
            urllib.request.Request(
                url,
                data=json.dumps({"type": "function"}).encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json"},
            ),
            timeout=1.0,
        ):
            raise AssertionError("expected 400")
    except urllib.error.HTTPError as exc:
        assert exc.code == 400
        body = json.loads(exc.read().decode("utf-8"))
        assert "error" in body
    finally:
        server.stop()


def test_post_invalid_type_or_capture_mode_returns_400():
    registry = BreakpointRegistry()
    server = AgentControlServer(registry, host="127.0.0.1", port=0)
    server.start()
    try:
        _wait_for_server(server)
        url = _base_url(server)
        for payload in (
            {"type": "unknown", "value": "add"},
            {"type": "function", "value": "add", "capture_mode": "ALWAYS"},
            {"type": "file_line", "file": "x.py"},
        ):
            try:
                _post_json(url, payload)
                raise AssertionError(f"expected 400 for {payload}")
            except urllib.error.HTTPError as exc:
                assert exc.code == 400
    finally:
        server.stop()


def test_post_malformed_json_returns_400():
    registry = BreakpointRegistry()
    server = AgentControlServer(registry, host="127.0.0.1", port=0)
    server.start()
    try:
        _wait_for_server(server)
        assert _post_raw(_base_url(server), b"{not-json") == 400
    finally:
        server.stop()


def test_control_server_unknown_route_returns_404():
    registry = BreakpointRegistry()
    server = AgentControlServer(registry, host="127.0.0.1", port=0)
    server.start()
    try:
        _wait_for_server(server)
        with urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}/health",
            timeout=1.0,
        ):
            pass
        raise AssertionError("expected HTTP 404")
    except urllib.error.HTTPError as exc:
        assert exc.code == 404
    finally:
        server.stop()


def test_control_server_exposes_registry():
    registry = BreakpointRegistry()
    server = AgentControlServer(registry, host="127.0.0.1", port=0)
    assert server.registry is registry
