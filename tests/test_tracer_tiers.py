import queue
import sys
from pathlib import Path

from agent.breakpoints import normalize_path
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


def test_global_trace_does_no_work_on_line_events():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-line",
            type=BreakpointType.FILE_LINE,
            file=str(ADDITION_ENGINE_FILE),
            line=5,
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue()
    tracer = Tracer(registry, capture_queue)
    frame = sys._getframe()

    assert tracer.global_trace(frame, "line", None) is None
    assert capture_queue.empty()


def test_global_trace_does_no_work_on_return_events():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-return-fn",
            type=BreakpointType.FUNCTION,
            value="tracked",
            capture_mode=CaptureMode.RETURN,
        )
    )
    capture_queue = create_capture_queue()
    tracer = Tracer(registry, capture_queue)
    frame = sys._getframe()

    assert tracer.global_trace(frame, "return", 42) is None
    assert capture_queue.empty()


def test_function_return_local_trace_does_not_emit_line_events():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-return-fn",
            type=BreakpointType.FUNCTION,
            value="multi_line_fn",
            capture_mode=CaptureMode.RETURN,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def multi_line_fn() -> int:
        total = 0
        total += 1
        total += 2
        return total

    _run_with_tracer(tracer, multi_line_fn)
    captured = _drain_queue(capture_queue)

    assert len(captured) == 1
    assert captured[0].event == TraceEvent.RETURN
    assert all(item.event != TraceEvent.LINE for item in captured)


def test_function_entry_does_not_install_line_tracing_without_watched_file():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-entry-fn",
            type=BreakpointType.FUNCTION,
            value="multi_line_fn",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def multi_line_fn() -> int:
        total = 0
        total += 1
        return total

    _run_with_tracer(tracer, multi_line_fn)
    captured = _drain_queue(capture_queue)

    assert len(captured) == 1
    assert captured[0].event == TraceEvent.CALL
    assert all(item.event != TraceEvent.LINE for item in captured)


def test_file_line_both_captures_line_and_return():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-line-both",
            type=BreakpointType.FILE_LINE,
            file=str(ADDITION_ENGINE_FILE),
            line=5,
            capture_mode=CaptureMode.BOTH,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    _run_with_tracer(tracer, lambda: AdditionEngine().add(6.0, 7.0))
    captured = _drain_queue(capture_queue)

    events = {(item.breakpoint_id, item.event) for item in captured}
    assert ("bp-line-both", TraceEvent.LINE) in events
    assert ("bp-line-both", TraceEvent.RETURN) in events
    return_capture = next(
        item for item in captured if item.event == TraceEvent.RETURN
    )
    assert return_capture.return_value == 13.0


def test_file_line_breakpoint_does_not_fire_on_wrong_line():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-wrong-line",
            type=BreakpointType.FILE_LINE,
            file=str(ADDITION_ENGINE_FILE),
            line=999,
            capture_mode=CaptureMode.BOTH,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    _run_with_tracer(tracer, lambda: AdditionEngine().add(1.0, 2.0))
    assert capture_queue.empty()


def test_file_line_local_trace_captures_entry_on_matching_line():
    registry = BreakpointRegistry()
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

    _run_with_tracer(tracer, lambda: AdditionEngine().add(1.0, 2.0))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 1
    assert captured[0].breakpoint_id == "bp-line-entry"
    assert captured[0].event == TraceEvent.LINE
    assert captured[0].frames[0].line == 5
    assert captured[0].frames[0].locals["a"] == 1.0


def test_file_line_local_trace_captures_return_on_matching_line():
    registry = BreakpointRegistry()
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

    _run_with_tracer(tracer, lambda: AdditionEngine().add(3.0, 4.0))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 1
    assert captured[0].breakpoint_id == "bp-line-return"
    assert captured[0].event == TraceEvent.RETURN
    assert captured[0].return_value == 7.0
    assert captured[0].frames[0].line == 5


def test_file_line_trace_only_in_watched_files():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-line",
            type=BreakpointType.FILE_LINE,
            file=str(ADDITION_ENGINE_FILE),
            line=5,
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    def helper() -> int:
        return 99

    _run_with_tracer(tracer, helper)
    assert capture_queue.empty()


def test_watched_files_use_normalized_paths():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-line",
            type=BreakpointType.FILE_LINE,
            file="target/engines/addition.py",
            line=5,
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    _run_with_tracer(tracer, lambda: AdditionEngine().add(2.0, 3.0))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 1
    assert normalize_path(ADDITION_ENGINE_FILE) in registry.watched_files()
