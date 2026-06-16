"""Synchronous RawCapture extraction from live frames (ARCHITECTURE_V2 §5.5)."""

from __future__ import annotations

import threading
import time
import types
from typing import Any

from agent.breakpoints import normalize_path
from agent.models import RawCapture, RawFrame, TraceEvent


def capture_stack_frames(frame: types.FrameType) -> tuple[RawFrame, ...]:
    """Walk the ``f_back`` chain; innermost frame first (index 0)."""
    frames: list[RawFrame] = []
    current: types.FrameType | None = frame
    while current is not None:
        code = current.f_code
        frames.append(
            RawFrame(
                function=code.co_name,
                qualname=code.co_qualname or None,
                file=normalize_path(code.co_filename),
                line=current.f_lineno,
                locals=dict(current.f_locals),
            )
        )
        current = current.f_back
    return tuple(frames)


def capture_raw(
    frame: types.FrameType,
    *,
    breakpoint_id: str,
    event: TraceEvent | str,
    return_value: Any | None = None,
    timestamp: float | None = None,
    thread_id: int | None = None,
) -> RawCapture:
    """Build an immutable RawCapture from the current trace frame."""
    trace_event = event if isinstance(event, TraceEvent) else TraceEvent(event)
    resolved_return = return_value if trace_event == TraceEvent.RETURN else None

    return RawCapture(
        breakpoint_id=breakpoint_id,
        event=trace_event,
        thread_id=thread_id if thread_id is not None else threading.get_ident(),
        timestamp=timestamp if timestamp is not None else time.monotonic(),
        frames=capture_stack_frames(frame),
        return_value=resolved_return,
    )
