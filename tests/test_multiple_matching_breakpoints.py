"""R20 — multiple breakpoints on the same target produce distinct snapshots."""

import json
import queue

from agent.installer import install_trace, remove_trace
from agent.models import Breakpoint, BreakpointType, CaptureMode, TraceEvent
from agent.registry import BreakpointRegistry
from agent.tracer import Tracer
from agent.worker import SnapshotWorker, create_capture_queue


class _MetricEngine:
    def score(self, base: int) -> int:
        total = base + 10
        return total


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


def test_two_function_entry_breakpoints_enqueue_distinct_captures():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-fn-a",
            type=BreakpointType.FUNCTION,
            value="measure",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    registry.register(
        Breakpoint(
            id="bp-fn-b",
            type=BreakpointType.FUNCTION,
            value="measure",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def measure(value: int) -> int:
        return value * 2

    _run_with_tracer(tracer, lambda: measure(4))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 2
    assert {item.breakpoint_id for item in captured} == {"bp-fn-a", "bp-fn-b"}
    assert all(item.event == TraceEvent.CALL for item in captured)


def test_two_function_entry_breakpoints_produce_two_snapshot_json_files(tmp_path):
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-json-a",
            type=BreakpointType.FUNCTION,
            value="report",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    registry.register(
        Breakpoint(
            id="bp-json-b",
            type=BreakpointType.FUNCTION,
            value="report",
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

    def report(seed: int) -> int:
        return seed + 1

    _run_with_tracer(tracer, lambda: report(7))
    capture_queue.join()
    worker.stop()

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 2
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in files]
    assert {item["breakpoint_id"] for item in payloads} == {"bp-json-a", "bp-json-b"}
    assert all(item["event"] == "call" for item in payloads)


def test_two_method_breakpoints_same_qualname_produce_distinct_snapshots(tmp_path):
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-method-a",
            type=BreakpointType.METHOD,
            value="_MetricEngine.score",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    registry.register(
        Breakpoint(
            id="bp-method-b",
            type=BreakpointType.METHOD,
            value="_MetricEngine.score",
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

    _run_with_tracer(tracer, lambda: _MetricEngine().score(5))
    capture_queue.join()
    worker.stop()

    payloads = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in tmp_path.glob("*.json")
    ]
    assert len(payloads) == 2
    assert {item["breakpoint_id"] for item in payloads} == {
        "bp-method-a",
        "bp-method-b",
    }
    assert all(
        item["stack_frames"][0]["qualname"] == "_MetricEngine.score"
        for item in payloads
    )


def test_entry_and_return_breakpoints_same_function_produce_distinct_snapshots():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-entry",
            type=BreakpointType.FUNCTION,
            value="merge",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    registry.register(
        Breakpoint(
            id="bp-return",
            type=BreakpointType.FUNCTION,
            value="merge",
            capture_mode=CaptureMode.RETURN,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def merge(left: int, right: int) -> int:
        combined = left + right
        return combined

    _run_with_tracer(tracer, lambda: merge(3, 4))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 2
    by_id = {item.breakpoint_id: item for item in captured}
    assert set(by_id) == {"bp-entry", "bp-return"}
    assert by_id["bp-entry"].event == TraceEvent.CALL
    assert by_id["bp-return"].event == TraceEvent.RETURN
    assert by_id["bp-return"].return_value == 7


def test_two_both_breakpoints_same_function_produce_four_distinct_captures():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-both-1",
            type=BreakpointType.FUNCTION,
            value="double",
            capture_mode=CaptureMode.BOTH,
        )
    )
    registry.register(
        Breakpoint(
            id="bp-both-2",
            type=BreakpointType.FUNCTION,
            value="double",
            capture_mode=CaptureMode.BOTH,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def double(n: int) -> int:
        return n * 2

    _run_with_tracer(tracer, lambda: double(6))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 4
    by_id: dict[str, list] = {}
    for item in captured:
        by_id.setdefault(item.breakpoint_id, []).append(item.event)
    assert set(by_id) == {"bp-both-1", "bp-both-2"}
    assert all(
        set(events) == {TraceEvent.CALL, TraceEvent.RETURN}
        for events in by_id.values()
    )
