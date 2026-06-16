import json
import queue
import types

from agent.installer import install_trace, remove_trace
from agent.models import Breakpoint, BreakpointType, CaptureMode, TraceEvent
from agent.registry import BreakpointRegistry
from agent.tracer import Tracer
from agent.worker import SnapshotWorker, create_capture_queue


class _MethodReturnEngine:
    def mul(self, a: int, b: int) -> int:
        product = a * b
        return product


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


def test_return_capture_includes_final_locals_and_return_value():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-return",
            type=BreakpointType.FUNCTION,
            value="accumulate",
            capture_mode=CaptureMode.RETURN,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def accumulate(base: int) -> int:
        total = base
        total += 10
        return total

    _run_with_tracer(tracer, lambda: accumulate(5))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 1
    raw = captured[0]
    assert raw.event == TraceEvent.RETURN
    assert raw.return_value == 15
    assert raw.frames[0].locals["total"] == 15
    assert raw.frames[0].function == "accumulate"


def test_both_mode_produces_call_and_return_captures():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-both",
            type=BreakpointType.FUNCTION,
            value="scale",
            capture_mode=CaptureMode.BOTH,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def scale(value: int) -> int:
        factor = 3
        return value * factor

    _run_with_tracer(tracer, lambda: scale(4))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 2
    call_capture = next(item for item in captured if item.event == TraceEvent.CALL)
    return_capture = next(item for item in captured if item.event == TraceEvent.RETURN)
    assert call_capture.breakpoint_id == "bp-both"
    assert return_capture.breakpoint_id == "bp-both"
    assert call_capture.return_value is None
    assert return_capture.return_value == 12
    assert return_capture.frames[0].locals["factor"] == 3


def test_return_capture_for_multiple_breakpoints_same_function():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-return-1",
            type=BreakpointType.FUNCTION,
            value="finish",
            capture_mode=CaptureMode.RETURN,
        )
    )
    registry.register(
        Breakpoint(
            id="bp-return-2",
            type=BreakpointType.FUNCTION,
            value="finish",
            capture_mode=CaptureMode.RETURN,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def finish() -> str:
        status = "ok"
        return status

    _run_with_tracer(tracer, finish)
    captured = _drain_queue(capture_queue)

    assert len(captured) == 2
    assert {item.breakpoint_id for item in captured} == {"bp-return-1", "bp-return-2"}
    assert all(item.event == TraceEvent.RETURN for item in captured)
    assert all(item.return_value == "ok" for item in captured)


def test_queued_raw_capture_has_no_frame_references():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-return",
            type=BreakpointType.FUNCTION,
            value="payload",
            capture_mode=CaptureMode.RETURN,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def payload() -> dict[str, int]:
        data = {"x": 1}
        return data

    _run_with_tracer(tracer, payload)
    captured = _drain_queue(capture_queue)

    raw = captured[0]
    assert raw.return_value == {"x": 1}
    assert isinstance(raw.frames[0].locals, dict)
    assert "data" in raw.frames[0].locals


def test_return_mode_produces_no_call_events():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-return-only",
            type=BreakpointType.FUNCTION,
            value="silent_entry",
            capture_mode=CaptureMode.RETURN,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def silent_entry(value: int) -> int:
        doubled = value * 2
        return doubled

    _run_with_tracer(tracer, lambda: silent_entry(6))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 1
    assert captured[0].event == TraceEvent.RETURN
    assert all(item.event != TraceEvent.CALL for item in captured)


def test_both_mode_call_and_return_locals_differ():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-both-locals",
            type=BreakpointType.FUNCTION,
            value="evolve",
            capture_mode=CaptureMode.BOTH,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def evolve(seed: int) -> int:
        running = seed
        running += 5
        return running

    _run_with_tracer(tracer, lambda: evolve(3))
    captured = _drain_queue(capture_queue)

    call_capture = next(item for item in captured if item.event == TraceEvent.CALL)
    return_capture = next(item for item in captured if item.event == TraceEvent.RETURN)

    call_locals = call_capture.frames[0].locals
    return_locals = return_capture.frames[0].locals
    assert call_locals["seed"] == 3
    assert "running" not in call_locals
    assert return_locals["running"] == 8
    assert return_capture.return_value == 8


def test_method_return_breakpoint_captures_qualname_and_return_value():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-method-return",
            type=BreakpointType.METHOD,
            value="_MethodReturnEngine.mul",
            capture_mode=CaptureMode.RETURN,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    _run_with_tracer(tracer, lambda: _MethodReturnEngine().mul(4, 5))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 1
    raw = captured[0]
    assert raw.event == TraceEvent.RETURN
    assert raw.return_value == 20
    assert raw.frames[0].qualname == "_MethodReturnEngine.mul"
    assert raw.frames[0].locals["product"] == 20


def test_queued_return_capture_has_no_live_frame_references():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-return",
            type=BreakpointType.FUNCTION,
            value="boxed",
            capture_mode=CaptureMode.RETURN,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def boxed() -> list[int]:
        values = [1, 2, 3]
        return values

    _run_with_tracer(tracer, boxed)
    captured = _drain_queue(capture_queue)

    raw = captured[0]
    for frame in raw.frames:
        assert isinstance(frame.locals, dict)
        assert not isinstance(frame.locals, types.FrameType)
    assert raw.return_value == [1, 2, 3]


def test_return_hit_produces_snapshot_json_with_return_value(tmp_path):
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-return-json",
            type=BreakpointType.FUNCTION,
            value="finalize",
            capture_mode=CaptureMode.RETURN,
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

    def finalize(base: int) -> int:
        total = base + 7
        return total

    _run_with_tracer(tracer, lambda: finalize(5))
    capture_queue.join()
    worker.stop()

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    payload = json.loads(files[0].read_text(encoding="utf-8"))
    assert payload["breakpoint_id"] == "bp-return-json"
    assert payload["event"] == "return"
    assert payload["capture_mode"] == "RETURN"
    assert payload["return_value"] == 12
    assert payload["stack_frames"][0]["locals"]["total"] == 12


def test_both_hit_produces_two_snapshot_json_files(tmp_path):
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-both-json",
            type=BreakpointType.FUNCTION,
            value="twice",
            capture_mode=CaptureMode.BOTH,
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

    def twice(n: int) -> int:
        return n * 2

    _run_with_tracer(tracer, lambda: twice(9))
    capture_queue.join()
    worker.stop()

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 2
    payloads = [
        json.loads(path.read_text(encoding="utf-8")) for path in files
    ]
    assert {item["event"] for item in payloads} == {"call", "return"}
    return_payload = next(item for item in payloads if item["event"] == "return")
    assert return_payload["return_value"] == 18
