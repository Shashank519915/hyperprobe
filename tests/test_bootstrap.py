"""End-to-end bootstrap smoke — HTTP request produces snapshot JSON (R1, R11)."""

import json
import threading
import time
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
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield runtime, port, tmp_path
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


def test_bootstrap_calculate_produces_snapshot_with_stack_frames(bootstrap_stack):
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

    assert files, "expected snapshot JSON after bootstrap calculate request"

    payloads = [
        json.loads(path.read_text(encoding="utf-8")) for path in files
    ]
    method_snapshots = [
        item for item in payloads if item.get("breakpoint_id") == "seed-method-add"
    ]
    assert method_snapshots, (
        "expected seed-method-add snapshot; got "
        f"{[item.get('breakpoint_id') for item in payloads]}"
    )

    snapshot = method_snapshots[0]
    assert snapshot["stack_frames"]
    qualnames = {frame.get("qualname") for frame in snapshot["stack_frames"]}
    assert "AdditionEngine.add" in qualnames


def test_bootstrap_control_api_lists_seed_breakpoints(bootstrap_stack):
    _runtime, _target_port, _snapshots_dir = bootstrap_stack
    control_port = _runtime.control_server.port

    status, payload = _http_get(
        control_port,
        BREAKPOINTS_PATH,
    )
    assert status == 200
    assert isinstance(payload, list)
    ids = {item["id"] for item in payload}
    assert "seed-method-add" in ids
