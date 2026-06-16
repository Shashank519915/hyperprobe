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


def test_control_server_breakpoints_route_returns_not_implemented():
    registry = BreakpointRegistry()
    server = AgentControlServer(registry, host="127.0.0.1", port=0)
    server.start()
    try:
        _wait_for_server(server)
        with urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}{BREAKPOINTS_PATH}",
            timeout=1.0,
        ):
            pass
        raise AssertionError("expected HTTP 501")
    except urllib.error.HTTPError as exc:
        assert exc.code == 501
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
