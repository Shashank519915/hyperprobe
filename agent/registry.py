import threading

from agent.breakpoints import normalize_path
from agent.models import Breakpoint, BreakpointType, TraceEvent


class BreakpointRegistry:
    """Thread-safe breakpoint store with O(1) lookup indexes (ARCHITECTURE_V2 §5.6)."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._breakpoints: dict[str, Breakpoint] = {}
        self._rebuild_indexes()

    def register(self, bp: Breakpoint) -> None:
        with self._lock:
            self._breakpoints[bp.id] = bp
            self._rebuild_indexes()

    def get(self, bp_id: str) -> Breakpoint | None:
        with self._lock:
            return self._breakpoints.get(bp_id)

    def list_all(self) -> list[Breakpoint]:
        with self._lock:
            return list(self._breakpoints.values())

    def has_any_function_or_method_bp(self) -> bool:
        with self._lock:
            return bool(self._function_names or self._method_qualnames)

    def function_names(self) -> set[str]:
        with self._lock:
            return set(self._function_names)

    def method_qualnames(self) -> set[str]:
        with self._lock:
            return set(self._method_qualnames)

    def watched_files(self) -> set[str]:
        with self._lock:
            return set(self._watched_files)

    def function_bps_by_name(self) -> dict[str, list[str]]:
        with self._lock:
            return {name: list(ids) for name, ids in self._function_bps_by_name.items()}

    def method_bps_by_qualname(self) -> dict[str, list[str]]:
        with self._lock:
            return {
                qualname: list(ids)
                for qualname, ids in self._method_bps_by_qualname.items()
            }

    def line_bps_by_file(self) -> dict[str, dict[int, list[str]]]:
        with self._lock:
            return {
                path: {line: list(ids) for line, ids in lines.items()}
                for path, lines in self._line_bps_by_file.items()
            }

    def get_function_breakpoint_ids(self, co_name: str) -> list[str]:
        with self._lock:
            return list(self._function_bps_by_name.get(co_name, []))

    def get_method_breakpoint_ids(self, co_qualname: str) -> list[str]:
        with self._lock:
            return list(self._method_bps_by_qualname.get(co_qualname, []))

    def get_line_breakpoint_ids(self, co_filename: str, lineno: int) -> list[str]:
        with self._lock:
            path = normalize_path(co_filename)
            return list(self._line_bps_by_file.get(path, {}).get(lineno, []))

    def get_matching_breakpoint_ids(
        self,
        *,
        co_name: str,
        co_qualname: str,
        co_filename: str,
        lineno: int,
        event: TraceEvent | str,
    ) -> list[str]:
        """Return all breakpoint ids matching this trace event — no deduplication (§5.3.1)."""
        event_name = event.value if isinstance(event, TraceEvent) else event
        with self._lock:
            if event_name == TraceEvent.CALL.value:
                matched: list[str] = []
                matched.extend(self._function_bps_by_name.get(co_name, []))
                matched.extend(self._method_bps_by_qualname.get(co_qualname, []))
                return matched
            if event_name == TraceEvent.LINE.value:
                path = normalize_path(co_filename)
                return list(self._line_bps_by_file.get(path, {}).get(lineno, []))
            return []

    def _rebuild_indexes(self) -> None:
        self._function_names: set[str] = set()
        self._method_qualnames: set[str] = set()
        self._watched_files: set[str] = set()
        self._function_bps_by_name: dict[str, list[str]] = {}
        self._method_bps_by_qualname: dict[str, list[str]] = {}
        self._line_bps_by_file: dict[str, dict[int, list[str]]] = {}

        for bp in self._breakpoints.values():
            match bp.type:
                case BreakpointType.FUNCTION:
                    if bp.value is None:
                        continue
                    self._function_names.add(bp.value)
                    self._function_bps_by_name.setdefault(bp.value, []).append(bp.id)
                case BreakpointType.METHOD:
                    if bp.value is None:
                        continue
                    self._method_qualnames.add(bp.value)
                    self._method_bps_by_qualname.setdefault(bp.value, []).append(
                        bp.id
                    )
                case BreakpointType.FILE_LINE:
                    if bp.file is None or bp.line is None:
                        continue
                    path = normalize_path(bp.file)
                    self._watched_files.add(path)
                    file_lines = self._line_bps_by_file.setdefault(path, {})
                    file_lines.setdefault(bp.line, []).append(bp.id)
