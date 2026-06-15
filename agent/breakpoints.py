from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import uuid4

import yaml

from agent.models import Breakpoint, BreakpointType, CaptureMode, TraceEvent

if TYPE_CHECKING:
    from agent.registry import BreakpointRegistry


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


def breakpoint_from_dict(raw: dict[str, Any]) -> Breakpoint:
    bp_type = BreakpointType(str(raw["type"]))
    capture_raw = raw.get("capture_mode", CaptureMode.ENTRY.value)
    capture_mode = CaptureMode(str(capture_raw))
    bp_id = str(raw["id"]) if raw.get("id") else str(uuid4())

    match bp_type:
        case BreakpointType.FUNCTION | BreakpointType.METHOD:
            value = raw.get("value")
            if not value:
                raise ValueError(f"{bp_type.value} breakpoint requires value")
            return Breakpoint(
                id=bp_id,
                type=bp_type,
                capture_mode=capture_mode,
                value=str(value),
            )
        case BreakpointType.FILE_LINE:
            file = raw.get("file")
            line = raw.get("line")
            if not file or line is None:
                raise ValueError("file_line breakpoint requires file and line")
            return Breakpoint(
                id=bp_id,
                type=bp_type,
                capture_mode=capture_mode,
                file=str(file),
                line=int(line),
            )
    raise ValueError(f"unsupported breakpoint type: {bp_type}")


def load_breakpoints_yaml(
    path: str | Path,
    registry: BreakpointRegistry,
) -> list[Breakpoint]:
    """Load seed breakpoints from YAML into registry (ARCHITECTURE_V2 §5.4)."""
    yaml_path = Path(path)
    payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    if payload is None:
        raise ValueError(f"{yaml_path} is empty")
    items = payload if isinstance(payload, list) else payload.get("breakpoints")
    if not isinstance(items, list) or not items:
        raise ValueError(f"{yaml_path} must contain a breakpoint list")

    loaded: list[Breakpoint] = []
    for entry in items:
        if not isinstance(entry, dict):
            raise ValueError("each breakpoint entry must be a mapping")
        bp = breakpoint_from_dict(entry)
        registry.register(bp)
        loaded.append(bp)
    return loaded
