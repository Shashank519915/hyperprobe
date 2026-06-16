"""Background snapshot worker — serialize RawCapture and write JSON (§5.5, §5.7)."""

from __future__ import annotations

import json
import os
import queue
import sys
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from agent.models import (
    Breakpoint,
    CaptureMode,
    RawCapture,
    Snapshot,
    StackFrame,
)
from agent.registry import BreakpointRegistry
from agent.serializer import SafeSerializer


def breakpoint_payload(bp: Breakpoint | None, breakpoint_id: str) -> dict[str, Any]:
    if bp is None:
        return {"id": breakpoint_id, "missing": True}

    payload: dict[str, Any] = {"type": bp.type.value}
    if bp.value is not None:
        payload["value"] = bp.value
    if bp.file is not None:
        payload["file"] = bp.file
    if bp.line is not None:
        payload["line"] = bp.line
    return payload


def build_snapshot(
    raw: RawCapture,
    registry: BreakpointRegistry,
    *,
    serializer: SafeSerializer | None = None,
    snapshot_id: str | None = None,
    timestamp: str | None = None,
) -> Snapshot:
    """Build a Snapshot from copied frame data — never walks live frames."""
    safe = serializer or SafeSerializer()
    bp = registry.get(raw.breakpoint_id)
    stack_frames = [
        StackFrame(
            index=index,
            function=frame.function,
            qualname=frame.qualname,
            file=frame.file,
            line=frame.line,
            locals=safe.serialize_locals(frame.locals),
        )
        for index, frame in enumerate(raw.frames)
    ]
    return_value = (
        safe.serialize(raw.return_value) if raw.return_value is not None else None
    )
    return Snapshot(
        snapshot_id=snapshot_id or str(uuid4()),
        timestamp=timestamp or datetime.now(UTC).isoformat(),
        breakpoint_id=raw.breakpoint_id,
        breakpoint=breakpoint_payload(bp, raw.breakpoint_id),
        capture_mode=bp.capture_mode if bp is not None else CaptureMode.ENTRY,
        event=raw.event,
        thread_id=raw.thread_id,
        stack_frames=stack_frames,
        return_value=return_value,
    )


def snapshot_to_dict(snapshot: Snapshot) -> dict[str, Any]:
    return {
        "snapshot_id": snapshot.snapshot_id,
        "timestamp": snapshot.timestamp,
        "breakpoint_id": snapshot.breakpoint_id,
        "breakpoint": snapshot.breakpoint,
        "capture_mode": snapshot.capture_mode.value,
        "event": snapshot.event.value,
        "thread_id": snapshot.thread_id,
        "return_value": snapshot.return_value,
        "stack_frames": [
            {
                "index": frame.index,
                "function": frame.function,
                "qualname": frame.qualname,
                "file": frame.file,
                "line": frame.line,
                "locals": frame.locals,
            }
            for frame in snapshot.stack_frames
        ],
    }


class SnapshotWorker:
    """Consume RawCapture records from a queue and write JSON snapshots."""

    def __init__(
        self,
        capture_queue: queue.Queue[RawCapture],
        registry: BreakpointRegistry,
        *,
        output_dir: Path | str = "snapshots",
        serializer: SafeSerializer | None = None,
        emit_stdout: bool | None = None,
    ) -> None:
        self._queue = capture_queue
        self._registry = registry
        self._output_dir = Path(output_dir)
        self._serializer = serializer or SafeSerializer()
        if emit_stdout is None:
            emit_stdout = os.environ.get("EMIT_STDOUT", "").strip() in {
                "1",
                "true",
                "True",
                "yes",
            }
        self._emit_stdout = emit_stdout
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="SnapshotWorker",
            daemon=True,
        )
        self._thread.start()

    def stop(self, timeout: float | None = 5.0) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout)

    def process(self, raw: RawCapture) -> Path:
        """Process one capture synchronously (used by worker loop and tests)."""
        snapshot = build_snapshot(
            raw,
            self._registry,
            serializer=self._serializer,
        )
        payload = snapshot_to_dict(snapshot)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        path = self._output_dir / f"{snapshot.snapshot_id}.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
        if self._emit_stdout:
            print(json.dumps(payload), flush=True)
        return path

    def _run(self) -> None:
        sys.settrace(None)
        threading.settrace(None)
        while not self._stop.is_set():
            try:
                raw = self._queue.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                self.process(raw)
            except Exception as exc:
                print(f"snapshot worker error: {exc}", file=sys.stderr)
            finally:
                self._queue.task_done()
