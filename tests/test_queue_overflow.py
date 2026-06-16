"""R23 — bounded queue overflow drops snapshots without breaking target execution."""

import json
import queue

import pytest

from agent.installer import install_trace, remove_trace
from agent.models import Breakpoint, BreakpointType, CaptureMode, TraceEvent
from agent.registry import BreakpointRegistry
from agent.tracer import Tracer
from agent.worker import DropLogger, SnapshotWorker, create_capture_queue


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


def test_traced_function_completes_when_queue_is_full():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-entry",
            type=BreakpointType.FUNCTION,
            value="compute",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=1)
    drop_logger = DropLogger(min_interval_seconds=60.0)
    tracer = Tracer(registry, capture_queue, drop_logger=drop_logger)

    def compute(base: int) -> int:
        return base * 3

    results: list[int] = []
    for i in range(5):
        outcome: dict[str, int] = {}

        def invoke(n: int = i) -> None:
            outcome["value"] = compute(n)

        _run_with_tracer(tracer, invoke)
        results.append(outcome["value"])

    assert results == [0, 3, 6, 9, 12]
    assert capture_queue.qsize() == 1


def test_both_mode_return_succeeds_when_return_capture_dropped():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-both",
            type=BreakpointType.FUNCTION,
            value="scale",
            capture_mode=CaptureMode.BOTH,
        )
    )
    capture_queue = create_capture_queue(maxsize=1)
    drop_logger = DropLogger(min_interval_seconds=60.0)
    tracer = Tracer(registry, capture_queue, drop_logger=drop_logger)

    def scale(value: int) -> int:
        factor = 4
        return value * factor

    result = None

    def invoke() -> None:
        nonlocal result
        result = scale(7)

    _run_with_tracer(tracer, invoke)
    captured = _drain_queue(capture_queue)

    assert result == 28
    assert len(captured) == 1
    assert captured[0].event == TraceEvent.CALL


def test_nested_traced_calls_complete_under_overflow():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-outer",
            type=BreakpointType.FUNCTION,
            value="outer",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    registry.register(
        Breakpoint(
            id="bp-inner",
            type=BreakpointType.FUNCTION,
            value="inner",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=1)
    drop_logger = DropLogger(min_interval_seconds=60.0)
    tracer = Tracer(registry, capture_queue, drop_logger=drop_logger)

    def inner() -> int:
        return 10

    def outer() -> int:
        return inner() + 1

    result = None

    def invoke() -> None:
        nonlocal result
        result = outer()

    _run_with_tracer(tracer, invoke)

    assert result == 11
    assert capture_queue.qsize() == 1


def test_target_exception_propagates_when_queue_is_full():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-fail",
            type=BreakpointType.FUNCTION,
            value="failing",
            capture_mode=CaptureMode.BOTH,
        )
    )
    capture_queue = create_capture_queue(maxsize=1)
    drop_logger = DropLogger(min_interval_seconds=60.0)
    tracer = Tracer(registry, capture_queue, drop_logger=drop_logger)

    def failing() -> None:
        raise ValueError("expected target failure")

    with pytest.raises(ValueError, match="expected target failure"):
        _run_with_tracer(tracer, failing)


def test_overflow_emits_rate_limited_stderr_without_breaking_target(capsys):
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-spam",
            type=BreakpointType.FUNCTION,
            value="tick",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=1)
    drop_logger = DropLogger(min_interval_seconds=60.0)
    tracer = Tracer(registry, capture_queue, drop_logger=drop_logger)

    def tick(n: int) -> int:
        return n + 1

    for i in range(4):
        _run_with_tracer(tracer, lambda i=i: tick(i))

    captured = capsys.readouterr()
    assert captured.err.count("snapshot dropped: queue full") == 1
    assert capture_queue.qsize() == 1


def test_worker_processes_accepted_captures_after_overflow(tmp_path):
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-json",
            type=BreakpointType.FUNCTION,
            value="record",
            capture_mode=CaptureMode.ENTRY,
        )
    )
    capture_queue = create_capture_queue(maxsize=1)
    drop_logger = DropLogger(min_interval_seconds=60.0)
    tracer = Tracer(registry, capture_queue, drop_logger=drop_logger)

    def record(value: int) -> int:
        return value + 2

    _run_with_tracer(tracer, lambda: record(1))
    _run_with_tracer(tracer, lambda: record(2))

    worker = SnapshotWorker(
        capture_queue,
        registry,
        output_dir=tmp_path,
    )
    worker.start()
    capture_queue.join()
    worker.stop()

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    payload = json.loads(files[0].read_text(encoding="utf-8"))
    assert payload["breakpoint_id"] == "bp-json"
    assert payload["stack_frames"][0]["locals"]["value"] == 1
