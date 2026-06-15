from pathlib import Path

from agent.models import Breakpoint, BreakpointType, CaptureMode, TraceEvent


def normalize_path(path: str | Path) -> str:
    """Canonical absolute path for file_line matching (ARCHITECTURE_V2 §5.6)."""
    return str(Path(path).resolve())


def _event_name(event: TraceEvent | str) -> str:
    return event.value if isinstance(event, TraceEvent) else event


def matches_function_breakpoint(
    bp: Breakpoint,
    co_name: str,
    event: TraceEvent | str,
) -> bool:
    if bp.type != BreakpointType.FUNCTION or bp.value is None:
        return False
    return _event_name(event) == TraceEvent.CALL.value and co_name == bp.value


def matches_method_breakpoint(
    bp: Breakpoint,
    co_qualname: str,
    event: TraceEvent | str,
) -> bool:
    if bp.type != BreakpointType.METHOD or bp.value is None:
        return False
    return _event_name(event) == TraceEvent.CALL.value and co_qualname == bp.value


def matches_file_line_breakpoint(
    bp: Breakpoint,
    co_filename: str,
    lineno: int,
    event: TraceEvent | str,
) -> bool:
    if bp.type != BreakpointType.FILE_LINE or bp.file is None or bp.line is None:
        return False
    if _event_name(event) != TraceEvent.LINE.value:
        return False
    return normalize_path(co_filename) == normalize_path(bp.file) and lineno == bp.line


def matches_breakpoint(
    bp: Breakpoint,
    *,
    co_name: str,
    co_qualname: str,
    co_filename: str,
    lineno: int,
    event: TraceEvent | str,
) -> bool:
    match bp.type:
        case BreakpointType.FUNCTION:
            return matches_function_breakpoint(bp, co_name, event)
        case BreakpointType.METHOD:
            return matches_method_breakpoint(bp, co_qualname, event)
        case BreakpointType.FILE_LINE:
            return matches_file_line_breakpoint(bp, co_filename, lineno, event)
    return False
