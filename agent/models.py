from dataclasses import dataclass
from enum import Enum
from typing import Any


class BreakpointType(str, Enum):
    FUNCTION = "function"
    METHOD = "method"
    FILE_LINE = "file_line"


class CaptureMode(str, Enum):
    ENTRY = "ENTRY"
    RETURN = "RETURN"
    BOTH = "BOTH"


class TraceEvent(str, Enum):
    CALL = "call"
    RETURN = "return"
    LINE = "line"


@dataclass
class Breakpoint:
    """Registered trace target — see ARCHITECTURE_V2 §5.6."""

    id: str
    type: BreakpointType
    capture_mode: CaptureMode = CaptureMode.ENTRY
    value: str | None = None
    file: str | None = None
    line: int | None = None


@dataclass(frozen=True)
class RawFrame:
    """Shallow copy of one frame — no live frame references (§5.5)."""

    function: str
    qualname: str | None
    file: str
    line: int
    locals: dict[str, Any]


@dataclass(frozen=True)
class RawCapture:
    """Sync copy enqueued from trace callback — immutable, frame-free (§5.5)."""

    breakpoint_id: str
    event: TraceEvent
    thread_id: int
    timestamp: float
    frames: tuple[RawFrame, ...]
    return_value: Any | None = None


@dataclass
class StackFrame:
    """One frame in emitted snapshot JSON (§5.7)."""

    index: int
    function: str
    qualname: str | None
    file: str
    line: int
    locals: dict[str, Any]


@dataclass
class Snapshot:
    """Serialized snapshot written by worker (§5.7)."""

    snapshot_id: str
    timestamp: str
    breakpoint_id: str
    breakpoint: dict[str, Any]
    capture_mode: CaptureMode
    event: TraceEvent
    thread_id: int
    stack_frames: list[StackFrame]
    return_value: Any | None = None
