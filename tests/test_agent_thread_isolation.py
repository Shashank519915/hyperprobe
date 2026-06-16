import queue
import threading
import time
import urllib.error
import urllib.request

from agent.control_server import AgentControlServer
from agent.installer import disable_tracing_on_current_thread, install_trace, remove_trace
from agent.models import Breakpoint, BreakpointType, CaptureMode
from agent.registry import BreakpointRegistry
from agent.tracer import Tracer
from agent.worker import SnapshotWorker, create_capture_queue


def _drain_queue(capture_queue: queue.Queue) -> list:
    items = []
    while not capture_queue.empty():
        items.append(capture_queue.get_nowait())
        capture_queue.task_done()
    return items


def test_disable_tracing_on_current_thread_clears_hooks():
    seen: dict[str, object | None] = {}

    original_sys = __import__("sys").settrace
    original_thread = __import__("threading").settrace

    def record_sys(value: object | None) -> None:
        seen["sys"] = value
        original_sys(value)

    def record_thread(value: object | None) -> None:
        seen["threading"] = value
        original_thread(value)

    import sys

    sys.settrace = record_sys  # type: ignore[method-assign]
    threading.settrace = record_thread  # type: ignore[method-assign]
    try:

        def run_disable() -> None:
            disable_tracing_on_current_thread()

        thread = threading.Thread(target=run_disable, name="agent-thread")
        thread.start()
        thread.join()
    finally:
        sys.settrace = original_sys  # type: ignore[method-assign]
        threading.settrace = original_thread  # type: ignore[method-assign]

    assert seen.get("sys") is None
    assert seen.get("threading") is None


def test_worker_thread_does_not_emit_agent_self_snapshots(tmp_path):
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-worker",
            type=BreakpointType.FUNCTION,
            value="build_snapshot",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    registry.register(
        Breakpoint(
            id="bp-target",
            type=BreakpointType.FUNCTION,
            value="target_fn",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=100)
    tracer = Tracer(registry, capture_queue)
    worker = SnapshotWorker(
        capture_queue,
        registry,
        output_dir=tmp_path,
    )
    installer = install_trace(tracer.global_trace)
    try:

        def target_fn() -> int:
            return 42

        target_fn()
        captured = _drain_queue(capture_queue)
        assert len(captured) == 1
        assert captured[0].breakpoint_id == "bp-target"
        assert captured[0].frames[0].function == "target_fn"

        worker.start()
        capture_queue.put(captured[0])
        capture_queue.join()
        time.sleep(0.1)
        assert _drain_queue(capture_queue) == []
        assert all(
            frame.function != "build_snapshot"
            for item in captured
            for frame in item.frames
        )
    finally:
        worker.stop()
        remove_trace(installer)


def test_control_server_thread_disables_tracing():
    seen: dict[str, object | None] = {}
    original_sys = __import__("sys").settrace
    original_thread = __import__("threading").settrace

    def record_sys(value: object | None) -> None:
        seen["sys"] = value
        original_sys(value)

    def record_thread(value: object | None) -> None:
        seen["threading"] = value
        original_thread(value)

    import sys

    sys.settrace = record_sys  # type: ignore[method-assign]
    threading.settrace = record_thread  # type: ignore[method-assign]
    registry = BreakpointRegistry()
    server = AgentControlServer(registry, host="127.0.0.1", port=0)
    try:
        server.start()
        deadline = time.time() + 2.0
        while time.time() < deadline and server._server is None:  # noqa: SLF001
            time.sleep(0.01)
        assert server._server is not None  # noqa: SLF001
        assert seen.get("sys") is None
        assert seen.get("threading") is None
    finally:
        server.stop()
        sys.settrace = original_sys  # type: ignore[method-assign]
        threading.settrace = original_thread  # type: ignore[method-assign]


def test_control_server_serves_without_self_snapshots(tmp_path):
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-handler",
            type=BreakpointType.FUNCTION,
            value="do_GET",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=100)
    tracer = Tracer(registry, capture_queue)
    server = AgentControlServer(registry, host="127.0.0.1", port=0)
    installer = install_trace(tracer.global_trace)
    server.start()
    try:
        deadline = time.time() + 2.0
        while time.time() < deadline and server._server is None:  # noqa: SLF001
            time.sleep(0.01)
        assert server._server is not None  # noqa: SLF001

        with urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}/breakpoints",
            timeout=1.0,
        ):
            pass
    except urllib.error.HTTPError:
        pass
    finally:
        server.stop()
        remove_trace(installer)

    captured = _drain_queue(capture_queue)
    assert captured == []
