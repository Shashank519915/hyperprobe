"""R7, R22 — file_line breakpoints fire at exact normalized path + line."""

import json
import queue
from pathlib import Path

from agent.breakpoints import normalize_path
from agent.installer import install_trace, remove_trace
from agent.models import Breakpoint, BreakpointType, CaptureMode, TraceEvent
from agent.registry import BreakpointRegistry
from agent.tracer import Tracer
from agent.worker import SnapshotWorker, create_capture_queue
from target.engines.addition import AdditionEngine

REPO_ROOT = Path(__file__).resolve().parents[1]
ADDITION_ENGINE_FILE = REPO_ROOT / "target" / "engines" / "addition.py"
ADDITION_RETURN_LINE = 5


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


def test_file_line_entry_fires_at_exact_line_with_relative_path():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-line-entry",
            type=BreakpointType.FILE_LINE,
            file="target/engines/addition.py",
            line=ADDITION_RETURN_LINE,
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    _run_with_tracer(tracer, lambda: AdditionEngine().add(10.0, 5.0))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 1
    frame = captured[0].frames[0]
    assert captured[0].event == TraceEvent.LINE
    assert frame.line == ADDITION_RETURN_LINE
    assert frame.file == normalize_path(ADDITION_ENGINE_FILE)
    assert frame.locals["a"] == 10.0


def test_file_line_does_not_fire_on_non_executed_line():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-class-line",
            type=BreakpointType.FILE_LINE,
            file=str(ADDITION_ENGINE_FILE),
            line=1,
            capture_mode=CaptureMode.BOTH,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    _run_with_tracer(tracer, lambda: AdditionEngine().add(1.0, 2.0))
    assert capture_queue.empty()


def test_file_line_dot_segment_relative_path_installs_local_trace():
    registry = BreakpointRegistry()
    messy_path = "target/../target/engines/addition.py"
    registry.register(
        Breakpoint(
            id="bp-messy-path",
            type=BreakpointType.FILE_LINE,
            file=messy_path,
            line=ADDITION_RETURN_LINE,
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    assert normalize_path(messy_path) in registry.watched_files()

    _run_with_tracer(tracer, lambda: AdditionEngine().add(4.0, 6.0))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 1
    assert captured[0].frames[0].line == ADDITION_RETURN_LINE


def test_file_line_return_produces_snapshot_json_at_normalized_path(tmp_path):
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-line-return-json",
            type=BreakpointType.FILE_LINE,
            file="target/engines/addition.py",
            line=ADDITION_RETURN_LINE,
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

    _run_with_tracer(tracer, lambda: AdditionEngine().add(8.0, 7.0))
    capture_queue.join()
    worker.stop()

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    payload = json.loads(files[0].read_text(encoding="utf-8"))
    assert payload["breakpoint_id"] == "bp-line-return-json"
    assert payload["event"] == "return"
    assert payload["capture_mode"] == "RETURN"
    assert payload["return_value"] == 15.0
    top = payload["stack_frames"][0]
    assert top["line"] == ADDITION_RETURN_LINE
    assert top["file"] == normalize_path(ADDITION_ENGINE_FILE)


def test_file_line_absolute_path_in_breakpoint_matches_runtime_frame():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-abs-path",
            type=BreakpointType.FILE_LINE,
            file=str(ADDITION_ENGINE_FILE),
            line=ADDITION_RETURN_LINE,
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    _run_with_tracer(tracer, lambda: AdditionEngine().add(2.5, 2.5))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 1
    assert captured[0].frames[0].file == normalize_path(ADDITION_ENGINE_FILE)


def test_file_line_both_captures_line_and_return_on_configured_line():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-line-both",
            type=BreakpointType.FILE_LINE,
            file="target/engines/addition.py",
            line=ADDITION_RETURN_LINE,
            capture_mode=CaptureMode.BOTH,
        )
    )
    capture_queue = create_capture_queue(maxsize=10)
    tracer = Tracer(registry, capture_queue)

    _run_with_tracer(tracer, lambda: AdditionEngine().add(3.0, 9.0))
    captured = _drain_queue(capture_queue)

    assert len(captured) == 2
    by_event = {item.event: item for item in captured}
    assert set(by_event) == {TraceEvent.LINE, TraceEvent.RETURN}
    assert all(item.frames[0].line == ADDITION_RETURN_LINE for item in captured)
    assert by_event[TraceEvent.RETURN].return_value == 12.0
