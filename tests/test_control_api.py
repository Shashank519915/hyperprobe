"""Dynamic breakpoint registration via control API (R25, §5.13)."""

import json
import queue
import time
import urllib.request

from agent.control_server import BREAKPOINTS_PATH, AgentControlServer
from agent.installer import install_trace, remove_trace
from agent.registry import BreakpointRegistry
from agent.tracer import Tracer
from agent.worker import SnapshotWorker, create_capture_queue
from target.engines.addition import AdditionEngine


def _wait_for_server(server: AgentControlServer, timeout: float = 2.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline and server._server is None:  # noqa: SLF001
        time.sleep(0.01)
    assert server._server is not None  # noqa: SLF001


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


def _drain_queue(capture_queue: queue.Queue) -> list:
    items = []
    while not capture_queue.empty():
        items.append(capture_queue.get_nowait())
        capture_queue.task_done()
    return items


def test_dynamic_registration_via_control_api_produces_snapshot(tmp_path):
    """No matching BP → no snapshot → POST /breakpoints → same call → snapshot (R25)."""
    registry = BreakpointRegistry()
    capture_queue = create_capture_queue(maxsize=10)
    worker = SnapshotWorker(
        capture_queue,
        registry,
        output_dir=tmp_path,
    )
    tracer = Tracer(registry, capture_queue)
    server = AgentControlServer(registry, host="127.0.0.1", port=0)

    worker.start()
    server.start()
    installer = install_trace(tracer.global_trace)
    try:
        _wait_for_server(server)
        url = f"http://127.0.0.1:{server.port}{BREAKPOINTS_PATH}"

        def invoke_add() -> float:
            return AdditionEngine().add(10.0, 20.0)

        assert invoke_add() == 30.0
        assert _drain_queue(capture_queue) == []
        assert list(tmp_path.glob("*.json")) == []

        status, payload = _post_json(
            url,
            {
                "id": "bp-dynamic-add",
                "type": "method",
                "value": "AdditionEngine.add",
                "capture_mode": "ENTRY",
            },
        )
        assert status == 201
        assert payload["id"] == "bp-dynamic-add"
        assert len(registry.list_all()) == 1

        assert invoke_add() == 30.0
        capture_queue.join()
        assert _drain_queue(capture_queue) == []

        files = list(tmp_path.glob("*.json"))
        assert len(files) == 1
        snapshot = json.loads(files[0].read_text(encoding="utf-8"))
        assert snapshot["breakpoint_id"] == "bp-dynamic-add"
        assert snapshot["stack_frames"][0]["qualname"] == "AdditionEngine.add"
    finally:
        server.stop()
        worker.stop()
        remove_trace(installer)
