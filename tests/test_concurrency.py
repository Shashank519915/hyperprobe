"""Concurrent HTTP under trace — non-halting instrumentation (R13)."""

import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.client import HTTPConnection

import pytest

from agent.bootstrap import DEFAULT_BREAKPOINTS_PATH, start_agent
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


def test_concurrent_calculate_requests_complete_under_trace(bootstrap_stack):
    """Many parallel calculator requests finish with 200 while tracing is active."""
    _runtime, target_port, _snapshots_dir = bootstrap_stack
    paths = [
        f"/calculate?op=add&a={a}&b={b}"
        for a, b in ((i, i + 1) for i in range(24))
    ]

    def fetch(path: str) -> tuple[int, float]:
        status, body = _http_get(target_port, path)
        return status, body["result"]

    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(fetch, path) for path in paths]
        results = [future.result(timeout=10) for future in as_completed(futures)]

    elapsed = time.monotonic() - started
    assert elapsed < 10.0
    assert len(results) == len(paths)
    assert all(status == 200 for status, _ in results)
    assert all(isinstance(result, float) for _, result in results)


def test_concurrent_requests_still_produce_snapshots(bootstrap_stack):
    """Tracing under load still emits snapshots without blocking requests."""
    runtime, target_port, snapshots_dir = bootstrap_stack
    paths = [
        f"/calculate?op=add&a=10&b=20"
        for _ in range(16)
    ]

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda path: _http_get(target_port, path), paths))

    deadline = time.time() + 5.0
    files: list = []
    while time.time() < deadline:
        runtime.capture_queue.join()
        files = list(snapshots_dir.glob("*.json"))
        if files:
            break
        time.sleep(0.05)

    assert files, "expected at least one snapshot JSON under concurrent load"
