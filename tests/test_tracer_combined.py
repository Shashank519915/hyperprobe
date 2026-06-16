import queue
from pathlib import Path

from agent.installer import install_trace, remove_trace
from agent.models import Breakpoint, BreakpointType, CaptureMode, TraceEvent
from agent.registry import BreakpointRegistry
from agent.tracer import Tracer
from agent.worker import create_capture_queue
from target.engines.addition import AdditionEngine

REPO_ROOT = Path(__file__).resolve().parents[1]
ADDITION_ENGINE_FILE = REPO_ROOT / "target" / "engines" / "addition.py"


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


def test_combined_local_trace_captures_method_both_and_file_line_entry():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-method-both",
            type=BreakpointType.METHOD,
            value="AdditionEngine.add",
            capture_mode=CaptureMode.BOTH,
        )
    )
    registry.register(
        Breakpoint(
            id="bp-line-entry",
            type=BreakpointType.FILE_LINE,
            file=str(ADDITION_ENGINE_FILE),
            line=5,
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    _run_with_tracer(tracer, lambda: AdditionEngine().add(2.0, 3.0))
    captured = _drain_queue(capture_queue)

    events = {(item.breakpoint_id, item.event) for item in captured}
    assert ("bp-method-both", TraceEvent.CALL) in events
    assert ("bp-method-both", TraceEvent.RETURN) in events
    assert ("bp-line-entry", TraceEvent.LINE) in events
    assert len(captured) == 3


def test_combined_local_trace_captures_method_return_and_file_line_return():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-method-return",
            type=BreakpointType.METHOD,
            value="AdditionEngine.add",
            capture_mode=CaptureMode.RETURN,
        )
    )
    registry.register(
        Breakpoint(
            id="bp-line-return",
            type=BreakpointType.FILE_LINE,
            file=str(ADDITION_ENGINE_FILE),
            line=5,
            capture_mode=CaptureMode.RETURN,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    _run_with_tracer(tracer, lambda: AdditionEngine().add(4.0, 5.0))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 2
    by_id = {item.breakpoint_id: item for item in captured}
    assert by_id["bp-method-return"].event == TraceEvent.RETURN
    assert by_id["bp-method-return"].return_value == 9.0
    assert by_id["bp-line-return"].event == TraceEvent.RETURN
    assert by_id["bp-line-return"].return_value == 9.0


def test_combined_local_trace_fires_line_and_function_return_together():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-method-return",
            type=BreakpointType.METHOD,
            value="AdditionEngine.add",
            capture_mode=CaptureMode.RETURN,
        )
    )
    registry.register(
        Breakpoint(
            id="bp-line-entry",
            type=BreakpointType.FILE_LINE,
            file=str(ADDITION_ENGINE_FILE),
            line=5,
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    _run_with_tracer(tracer, lambda: AdditionEngine().add(1.0, 1.0))
    captured = _drain_queue(capture_queue)

    events = {(item.breakpoint_id, item.event) for item in captured}
    assert ("bp-method-return", TraceEvent.RETURN) in events
    assert ("bp-line-entry", TraceEvent.LINE) in events
