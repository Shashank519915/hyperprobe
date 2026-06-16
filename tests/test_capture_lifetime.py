import queue

from agent.installer import install_trace, remove_trace
from agent.models import Breakpoint, BreakpointType, CaptureMode, TraceEvent
from agent.registry import BreakpointRegistry
from agent.tracer import Tracer
from agent.worker import create_capture_queue


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
