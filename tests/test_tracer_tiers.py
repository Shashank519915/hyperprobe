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
