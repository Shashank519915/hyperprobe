"""Full HTTP integration — bootstrap, control API, calculator, snapshots (R1, R25)."""

import json
import threading
import time
import urllib.request
from http.client import HTTPConnection

import pytest

from agent.bootstrap import DEFAULT_BREAKPOINTS_PATH, start_agent
from agent.control_server import BREAKPOINTS_PATH
from target.server import create_server


def _wait_for_control(runtime, timeout: float = 2.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline and runtime.control_server._server is None:  # noqa: SLF001
        time.sleep(0.01)
    assert runtime.control_server._server is not None  # noqa: SLF001


@pytest.fixture
def bootstrap_stack(tmp_path):
    runtime = start_agent(
        breakpoints_path=DEFAULT_BREAKPOINTS_PATH,
        snapshots_dir=tmp_path,
        control_host="127.0.0.1",
        control_port=0,
    )
    _wait_for_control(runtime)
    server = create_server("127.0.0.1", 0)
    target_port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield runtime, target_port, tmp_path
    finally:
        server.shutdown()
        thread.join(timeout=2)
        runtime.shutdown()


def _http_get(port: int, path: str) -> tuple[int, dict]:
    conn = HTTPConnection("127.0.0.1", port, timeout=5)
    conn.request("GET", path)
    response = conn.getresponse()
    raw = response.read()
    conn.close()
    payload = json.loads(raw.decode("utf-8")) if raw else {}
    return response.status, payload


def _post_json(port: int, path: str, payload: object) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=2.0) as response:
        raw = response.read()
        body = json.loads(raw.decode("utf-8")) if raw else {}
        return response.status, body


def test_full_stack_calculate_and_seed_snapshots(bootstrap_stack):
    """End-to-end: traced calculate request produces snapshot JSON on disk."""
    runtime, target_port, snapshots_dir = bootstrap_stack

    status, body = _http_get(target_port, "/calculate?op=add&a=10&b=20")
    assert status == 200
    assert body["result"] == 30.0

    deadline = time.time() + 3.0
    files: list = []
    while time.time() < deadline:
        runtime.capture_queue.join()
        files = list(snapshots_dir.glob("*.json"))
        if files:
            break
        time.sleep(0.05)

    assert files
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in files]
    assert any(item.get("breakpoint_id") == "seed-method-add" for item in payloads)


def test_runtime_breakpoint_over_http_then_calculate_produces_snapshot(bootstrap_stack):
    """POST /breakpoints on :9090, then calculate on :8080 — new snapshot appears."""
    runtime, target_port, snapshots_dir = bootstrap_stack
    control_port = runtime.control_server.port

    status, body = _http_get(target_port, "/calculate?op=add&a=1&b=2")
    assert status == 200
    assert body["result"] == 3.0
    before = len(list(snapshots_dir.glob("*.json")))

    status, created = _post_json(
        control_port,
        BREAKPOINTS_PATH,
        {
            "id": "integration-bp-add",
            "type": "method",
            "value": "AdditionEngine.add",
            "capture_mode": "ENTRY",
        },
    )
    assert status == 201
    assert created["id"] == "integration-bp-add"

    status, body = _http_get(target_port, "/calculate?op=add&a=3&b=7")
    assert status == 200
    assert body["result"] == 10.0

    deadline = time.time() + 3.0
    while time.time() < deadline:
        runtime.capture_queue.join()
        if len(list(snapshots_dir.glob("*.json"))) > before:
            break
        time.sleep(0.05)

    payloads = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in snapshots_dir.glob("*.json")
    ]
    assert any(item.get("breakpoint_id") == "integration-bp-add" for item in payloads)
