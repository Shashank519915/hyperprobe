import json
import queue

import pytest

from agent.models import (
    Breakpoint,
    BreakpointType,
    CaptureMode,
    RawCapture,
    RawFrame,
    TraceEvent,
)
from agent.registry import BreakpointRegistry
from agent.worker import (
    DEFAULT_CAPTURE_QUEUE_MAXSIZE,
    DropLogger,
    SnapshotWorker,
    build_snapshot,
    create_capture_queue,
    enqueue_capture,
    snapshot_to_dict,
)


def _sample_raw(
    *,
    event: TraceEvent = TraceEvent.CALL,
    return_value: object | None = None,
) -> RawCapture:
    return RawCapture(
        breakpoint_id="bp-add",
        event=event,
        thread_id=42,
        timestamp=100.0,
        frames=(
            RawFrame(
                function="add",
                qualname="AdditionEngine.add",
                file="/app/target/engines/addition.py",
                line=5,
                locals={"a": 10, "b": 20, "fn": (lambda: None)},
            ),
            RawFrame(
                function="compute",
                qualname="MathService.compute",
                file="/app/target/services/math_service.py",
                line=12,
                locals={"op": "add"},
            ),
        ),
        return_value=return_value,
    )


@pytest.fixture
def registry_with_add_bp() -> BreakpointRegistry:
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="bp-add",
            type=BreakpointType.METHOD,
            value="AdditionEngine.add",
            capture_mode=CaptureMode.BOTH,
        )
    )
    return registry


def test_build_snapshot_includes_breakpoint_and_stack(registry_with_add_bp):
    snapshot = build_snapshot(
        _sample_raw(),
        registry_with_add_bp,
        snapshot_id="snap-1",
        timestamp="2026-06-16T12:00:00+00:00",
    )
    assert snapshot.snapshot_id == "snap-1"
    assert snapshot.timestamp == "2026-06-16T12:00:00+00:00"
    assert snapshot.breakpoint_id == "bp-add"
    assert snapshot.breakpoint == {
        "type": "method",
        "value": "AdditionEngine.add",
    }
    assert snapshot.capture_mode == CaptureMode.BOTH
    assert len(snapshot.stack_frames) == 2
    assert snapshot.stack_frames[0].index == 0
    assert snapshot.stack_frames[0].locals["a"] == 10
    assert snapshot.stack_frames[1].locals["op"] == "add"


def test_build_snapshot_serializes_locals_and_return_value(registry_with_add_bp):
    snapshot = build_snapshot(
        _sample_raw(event=TraceEvent.RETURN, return_value=30),
        registry_with_add_bp,
    )
    assert snapshot.event == TraceEvent.RETURN
    assert snapshot.return_value == 30
    assert snapshot.stack_frames[0].locals["fn"].startswith("<callable")


def test_snapshot_to_dict_uses_string_enums(registry_with_add_bp):
    payload = snapshot_to_dict(build_snapshot(_sample_raw(), registry_with_add_bp))
    assert payload["capture_mode"] == "BOTH"
    assert payload["event"] == "call"
    assert payload["stack_frames"][0]["index"] == 0


def test_worker_writes_json_file(tmp_path, registry_with_add_bp):
    capture_queue: queue.Queue = queue.Queue()
    worker = SnapshotWorker(
        capture_queue,
        registry_with_add_bp,
        output_dir=tmp_path,
    )
    worker.start()
    capture_queue.put(_sample_raw())
    capture_queue.join()
    worker.stop()

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text(encoding="utf-8"))
    assert data["breakpoint_id"] == "bp-add"
    assert data["stack_frames"][0]["locals"]["a"] == 10
    assert data["stack_frames"][1]["function"] == "compute"


def test_worker_emit_stdout(monkeypatch, tmp_path, registry_with_add_bp, capsys):
    monkeypatch.setenv("EMIT_STDOUT", "1")
    worker = SnapshotWorker(
        queue.Queue(),
        registry_with_add_bp,
        output_dir=tmp_path,
    )
    worker.process(_sample_raw())
    captured = capsys.readouterr()
    payload = json.loads(captured.out.strip())
    assert payload["breakpoint_id"] == "bp-add"


def test_worker_continues_after_processing_error(tmp_path, registry_with_add_bp):
    capture_queue: queue.Queue = queue.Queue()
    worker = SnapshotWorker(
        capture_queue,
        registry_with_add_bp,
        output_dir=tmp_path,
    )

    def boom(_raw: RawCapture) -> None:
        raise RuntimeError("write failed")

    worker.process = boom  # type: ignore[method-assign]
    worker.start()
    capture_queue.put(_sample_raw())
    capture_queue.join()
    worker.stop()
    assert list(tmp_path.glob("*.json")) == []


def test_worker_disables_tracing_in_worker_thread(registry_with_add_bp):
    capture_queue: queue.Queue = queue.Queue()
    worker = SnapshotWorker(capture_queue, registry_with_add_bp)
    seen: dict[str, object | None] = {}

    original_settrace = __import__("sys").settrace
    original_thread_settrace = __import__("threading").settrace

    def record_settrace(value: object | None) -> None:
        seen["sys"] = value
        original_settrace(value)

    def record_thread_settrace(value: object | None) -> None:
        seen["threading"] = value
        original_thread_settrace(value)

    import sys
    import threading

    sys.settrace = record_settrace  # type: ignore[method-assign]
    threading.settrace = record_thread_settrace  # type: ignore[method-assign]
    try:
        worker.start()
        capture_queue.put(_sample_raw())
        capture_queue.join()
        worker.stop()
    finally:
        sys.settrace = original_settrace  # type: ignore[method-assign]
        threading.settrace = original_thread_settrace  # type: ignore[method-assign]

    assert seen.get("sys") is None
    assert seen.get("threading") is None


def test_create_capture_queue_default_maxsize():
    capture_queue = create_capture_queue()
    assert capture_queue.maxsize == DEFAULT_CAPTURE_QUEUE_MAXSIZE


def test_enqueue_capture_accepts_until_full():
    capture_queue = create_capture_queue(maxsize=2)
    raw = _sample_raw()
    assert enqueue_capture(capture_queue, raw) is True
    assert enqueue_capture(capture_queue, raw) is True
    assert capture_queue.qsize() == 2


def test_enqueue_capture_drops_when_full_without_raising(capsys):
    capture_queue = create_capture_queue(maxsize=1)
    raw = _sample_raw()
    drop_logger = DropLogger(min_interval_seconds=60.0)

    assert enqueue_capture(capture_queue, raw, drop_logger=drop_logger) is True
    assert enqueue_capture(capture_queue, raw, drop_logger=drop_logger) is False
    assert capture_queue.qsize() == 1

    captured = capsys.readouterr()
    assert "snapshot dropped: queue full" in captured.err


def test_drop_logger_rate_limits_repeated_warnings(capsys):
    drop_logger = DropLogger(min_interval_seconds=60.0)
    for _ in range(5):
        drop_logger.warn_queue_full()

    captured = capsys.readouterr()
    assert captured.err.count("snapshot dropped: queue full") == 1


def test_drop_logger_reports_suppressed_count_after_interval(monkeypatch, capsys):
    drop_logger = DropLogger(min_interval_seconds=10.0)
    times = iter([0.0, 1.0, 11.0])

    monkeypatch.setattr("agent.worker.time.monotonic", lambda: next(times))

    drop_logger.warn_queue_full()
    drop_logger.warn_queue_full()
    drop_logger.warn_queue_full()

    captured = capsys.readouterr()
    lines = [line for line in captured.err.splitlines() if line]
    assert len(lines) == 2
    assert lines[0] == "snapshot dropped: queue full"
    assert lines[1] == "snapshot dropped: queue full (1 additional drops suppressed)"


def test_bounded_queue_with_worker_processes_accepted_only(
    tmp_path, registry_with_add_bp
):
    capture_queue = create_capture_queue(maxsize=1)
    worker = SnapshotWorker(
        capture_queue,
        registry_with_add_bp,
        output_dir=tmp_path,
    )
    drop_logger = DropLogger(min_interval_seconds=60.0)
    worker.start()

    first = _sample_raw()
    second = _sample_raw()
    assert enqueue_capture(capture_queue, first, drop_logger=drop_logger) is True
    assert enqueue_capture(capture_queue, second, drop_logger=drop_logger) is False

    capture_queue.join()
    worker.stop()

    assert len(list(tmp_path.glob("*.json"))) == 1

