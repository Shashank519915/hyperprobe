"""Two-tier sys.settrace callbacks (ARCHITECTURE_V2 §5.3)."""

from __future__ import annotations

import queue
import sys
import types
from typing import Any

from agent.breakpoints import normalize_path
from agent.capture import capture_raw
from agent.installer import TraceFunction
from agent.models import CaptureMode, RawCapture, TraceEvent
from agent.registry import BreakpointRegistry
from agent.worker import DropLogger, enqueue_capture


class Tracer:
    """Process-wide global trace with ENTRY capture on function/method hits."""

    def __init__(
        self,
        registry: BreakpointRegistry,
        capture_queue: queue.Queue[RawCapture],
        *,
        drop_logger: DropLogger | None = None,
    ) -> None:
        self._registry = registry
        self._capture_queue = capture_queue
        self._drop_logger = drop_logger
        self._frame_return_bps: dict[int, list[str]] = {}

    def global_trace(
        self,
        frame: types.FrameType,
        event: str,
        arg: Any,
    ) -> TraceFunction | None:
        try:
            if event != TraceEvent.CALL.value:
                return None
            return self._handle_call(frame)
        except BaseException as exc:
            print(f"global_trace error: {exc}", file=sys.stderr)
            return None

    def local_trace_for_function_breakpoint(
        self,
        frame: types.FrameType,
        event: str,
        arg: Any,
    ) -> TraceFunction | None:
        """Scoped trace for RETURN/BOTH — capture on ``'return'`` only (§5.3)."""
        try:
            if event != TraceEvent.RETURN.value:
                return self.local_trace_for_function_breakpoint
            bp_ids = self._frame_return_bps.pop(id(frame), [])
            for bp_id in bp_ids:
                self._enqueue(
                    frame,
                    bp_id,
                    TraceEvent.RETURN,
                    return_value=arg,
                )
            return None
        except BaseException as exc:
            print(f"local_trace error: {exc}", file=sys.stderr)
            return None

    def _handle_call(self, frame: types.FrameType) -> TraceFunction | None:
        code = frame.f_code
        path = normalize_path(code.co_filename)

        if (
            not self._registry.has_any_function_or_method_bp()
            and path not in self._registry.watched_files()
        ):
            return None

        bp_ids = self._registry.get_matching_breakpoint_ids(
            co_name=code.co_name,
            co_qualname=code.co_qualname,
            co_filename=code.co_filename,
            lineno=frame.f_lineno,
            event=TraceEvent.CALL,
        )

        local_trace_needed = False
        for bp_id in bp_ids:
            bp = self._registry.get(bp_id)
            if bp is None:
                continue
            if bp.capture_mode in (CaptureMode.ENTRY, CaptureMode.BOTH):
                self._enqueue(frame, bp_id, TraceEvent.CALL)
            if bp.capture_mode in (CaptureMode.RETURN, CaptureMode.BOTH):
                local_trace_needed = True

        if local_trace_needed:
            return_bps = self._return_breakpoint_ids(bp_ids)
            if return_bps:
                self._frame_return_bps[id(frame)] = return_bps
            return self.local_trace_for_function_breakpoint

        # file_line local trace — task 8.4
        return None

    def _return_breakpoint_ids(self, bp_ids: list[str]) -> list[str]:
        matched: list[str] = []
        for bp_id in bp_ids:
            bp = self._registry.get(bp_id)
            if bp is None:
                continue
            if bp.capture_mode in (CaptureMode.RETURN, CaptureMode.BOTH):
                matched.append(bp_id)
        return matched

    def _enqueue(
        self,
        frame: types.FrameType,
        breakpoint_id: str,
        event: TraceEvent,
        *,
        return_value: Any | None = None,
    ) -> None:
        raw = capture_raw(
            frame,
            breakpoint_id=breakpoint_id,
            event=event,
            return_value=return_value,
        )
        enqueue_capture(
            self._capture_queue,
            raw,
            drop_logger=self._drop_logger,
        )
