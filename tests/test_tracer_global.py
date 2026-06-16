import json
import queue
import sys

from agent.installer import install_trace, remove_trace
from agent.models import Breakpoint, BreakpointType, CaptureMode, TraceEvent
from agent.registry import BreakpointRegistry
from agent.tracer import Tracer
from agent.worker import SnapshotWorker, create_capture_queue


class _AdditionEngine:
    def add(self, a: int, b: int) -> int:
        return a + b


def _run_with_tracer(tracer: Tracer, target) -> None:
    installer = install_trace(tracer.global_trace)
    try:
        target()
    finally:
        remove_trace(installer)


def _drain_queue(capture_queue: queue.Queue) -> list:
    items = []
    while not capture_queue.empty():
        items.append(capture_queue.get_nowait())
        capture_queue.task_done()
    return items


def test_global_trace_returns_none_for_non_call_events():
    registry = BreakpointRegistry()
    capture_queue = create_capture_queue()
    tracer = Tracer(registry, capture_queue)
    frame = sys._getframe()

    assert tracer.global_trace(frame, "line", None) is None
    assert tracer.global_trace(frame, "return", None) is None
    assert capture_queue.empty()


def test_global_trace_fast_reject_when_no_breakpoints():
    registry = BreakpointRegistry()
    capture_queue = create_capture_queue()
    tracer = Tracer(registry, capture_queue)

    def unrelated() -> int:
        return 1

    _run_with_tracer(tracer, unrelated)
    assert capture_queue.empty()


def test_global_trace_entry_enqueues_raw_capture():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-add",
            type=BreakpointType.FUNCTION,
            value="add",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def add(a: int, b: int) -> int:
        return a + b

    _run_with_tracer(tracer, lambda: add(10, 20))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 1
    assert captured[0].breakpoint_id == "bp-add"
    assert captured[0].event == TraceEvent.CALL
    assert captured[0].frames[0].function == "add"
    assert captured[0].frames[0].locals["a"] == 10


def test_global_trace_entry_multiple_breakpoints_same_name():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-1",
            type=BreakpointType.FUNCTION,
            value="compute",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    registry.register(
        Breakpoint(
            id="bp-2",
            type=BreakpointType.FUNCTION,
            value="compute",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def compute(x: int) -> int:
        return x + 1

    _run_with_tracer(tracer, lambda: compute(5))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 2
    assert {item.breakpoint_id for item in captured} == {"bp-1", "bp-2"}


def test_global_trace_method_breakpoint_matches_qualname():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-method",
            type=BreakpointType.METHOD,
            value="_AdditionEngine.add",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    _run_with_tracer(tracer, lambda: _AdditionEngine().add(3, 4))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 1
    assert captured[0].breakpoint_id == "bp-method"
    assert captured[0].frames[0].qualname == "_AdditionEngine.add"


def test_global_trace_both_captures_on_call_and_installs_local_trace():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-both",
            type=BreakpointType.FUNCTION,
            value="tracked",
            capture_mode=CaptureMode.BOTH,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def tracked(value: int) -> int:
        return value * 2

    _run_with_tracer(tracer, lambda: tracked(7))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 2
    assert {item.event for item in captured} == {TraceEvent.CALL, TraceEvent.RETURN}
    assert all(item.breakpoint_id == "bp-both" for item in captured)
    return_capture = next(item for item in captured if item.event == TraceEvent.RETURN)
    assert return_capture.return_value == 14


def test_global_trace_return_mode_captures_on_return():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-return",
            type=BreakpointType.FUNCTION,
            value="later",
            capture_mode=CaptureMode.RETURN,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def later(x: int) -> int:
        result = x + 1
        return result

    _run_with_tracer(tracer, lambda: later(4))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 1
    assert captured[0].breakpoint_id == "bp-return"
    assert captured[0].event == TraceEvent.RETURN
    assert captured[0].return_value == 5
    assert captured[0].frames[0].locals["result"] == 5


def test_entry_hit_produces_snapshot_json(tmp_path):
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-add",
            type=BreakpointType.FUNCTION,
            value="add",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    worker = SnapshotWorker(
        capture_queue,
        registry,
        output_dir=tmp_path,
    )
    tracer = Tracer(registry, capture_queue)
    worker.start()

    def add(a: int, b: int) -> int:
        return a + b

    _run_with_tracer(tracer, lambda: add(2, 3))
    capture_queue.join()
    worker.stop()

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    payload = json.loads(files[0].read_text(encoding="utf-8"))
    assert payload["breakpoint_id"] == "bp-add"
    assert payload["stack_frames"][0]["locals"]["a"] == 2
