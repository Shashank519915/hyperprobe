import json
import threading
from http.client import HTTPConnection

import pytest

from target.server import create_server


@pytest.fixture
def calculator_server() -> int:
    server = create_server("127.0.0.1", 0)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        server.shutdown()
        thread.join(timeout=2)


def _http_get(port: int, path: str) -> tuple[int, dict]:
    conn = HTTPConnection("127.0.0.1", port, timeout=5)
    conn.request("GET", path)
    response = conn.getresponse()
    raw = response.read()
    conn.close()
    payload = json.loads(raw.decode("utf-8")) if raw else {}
    return response.status, payload


def test_calculate_add_returns_json(calculator_server: int):
    status, body = _http_get(
        calculator_server, "/calculate?op=add&a=10&b=20"
    )
    assert status == 200
    assert body == {"op": "add", "a": 10.0, "b": 20.0, "result": 30.0}


def test_calculate_sub_mul_div(calculator_server: int):
    cases = [
        ("sub", 10, 3, 7.0),
        ("mul", 4, 5, 20.0),
        ("div", 20, 4, 5.0),
    ]
    for op, a, b, expected in cases:
        status, body = _http_get(
            calculator_server, f"/calculate?op={op}&a={a}&b={b}"
        )
        assert status == 200
        assert body["result"] == expected


def test_calculate_missing_parameter_returns_400(calculator_server: int):
    status, body = _http_get(calculator_server, "/calculate?op=add&a=10")
    assert status == 400
    assert "error" in body


def test_calculate_unsupported_op_returns_400(calculator_server: int):
    status, body = _http_get(calculator_server, "/calculate?op=pow&a=2&b=3")
    assert status == 400
    assert "unsupported operation" in body["error"]


def test_calculate_divide_by_zero_returns_400(calculator_server: int):
    status, body = _http_get(
        calculator_server, "/calculate?op=div&a=10&b=0"
    )
    assert status == 400
    assert body["error"] == "division by zero"


def test_unknown_path_returns_404(calculator_server: int):
    status, body = _http_get(calculator_server, "/unknown")
    assert status == 404
    assert body["error"] == "not found"


def test_target_tree_has_no_agent_imports():
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[1] / "target"
    forbidden = ("import agent", "from agent")
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            assert not any(token in stripped for token in forbidden), path
