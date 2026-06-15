from pathlib import Path

from agent.models import Breakpoint, BreakpointType, CaptureMode, TraceEvent
from agent.registry import BreakpointRegistry

REPO_ROOT = Path(__file__).resolve().parents[1]
ADDITION_ENGINE_FILE = REPO_ROOT / "target" / "engines" / "addition.py"


def test_empty_registry_has_no_function_or_method_breakpoints():
    registry = BreakpointRegistry()
    assert registry.has_any_function_or_method_bp() is False
    assert registry.function_names() == set()
    assert registry.watched_files() == set()


def test_register_function_breakpoint_builds_name_index():
    registry = BreakpointRegistry()
    bp = Breakpoint(id="fn-1", type=BreakpointType.FUNCTION, value="compute")
    registry.register(bp)

    assert registry.has_any_function_or_method_bp() is True
    assert registry.function_names() == {"compute"}
    assert registry.get_function_breakpoint_ids("compute") == ["fn-1"]
    assert registry.get("fn-1") == bp


def test_register_method_breakpoint_builds_qualname_index():
    registry = BreakpointRegistry()
    bp = Breakpoint(
        id="method-1",
        type=BreakpointType.METHOD,
        value="AdditionEngine.add",
    )
    registry.register(bp)

    assert registry.method_qualnames() == {"AdditionEngine.add"}
    assert registry.get_method_breakpoint_ids("AdditionEngine.add") == ["method-1"]


def test_register_file_line_breakpoint_builds_watched_file_index():
    registry = BreakpointRegistry()
    bp = Breakpoint(
        id="line-1",
        type=BreakpointType.FILE_LINE,
        file="target/engines/addition.py",
        line=5,
    )
    registry.register(bp)

    normalized = str(ADDITION_ENGINE_FILE.resolve())
    assert registry.watched_files() == {normalized}
    assert registry.get_line_breakpoint_ids(str(ADDITION_ENGINE_FILE), 5) == ["line-1"]
    assert registry.get_line_breakpoint_ids("target/engines/addition.py", 5) == [
        "line-1"
    ]


def test_register_upserts_by_id_and_rebuilds_indexes():
    registry = BreakpointRegistry()
    original = Breakpoint(id="fn-1", type=BreakpointType.FUNCTION, value="add")
    updated = Breakpoint(
        id="fn-1",
        type=BreakpointType.FUNCTION,
        value="compute",
        capture_mode=CaptureMode.RETURN,
    )
    registry.register(original)
    registry.register(updated)

    assert registry.get("fn-1") == updated
    assert registry.function_names() == {"compute"}
    assert registry.get_function_breakpoint_ids("add") == []
    assert registry.get_function_breakpoint_ids("compute") == ["fn-1"]


def test_multiple_function_breakpoints_same_name_return_all_ids():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(id="fn-entry", type=BreakpointType.FUNCTION, value="add")
    )
    registry.register(
        Breakpoint(
            id="fn-return",
            type=BreakpointType.FUNCTION,
            value="add",
            capture_mode=CaptureMode.RETURN,
        )
    )

    assert registry.get_function_breakpoint_ids("add") == ["fn-entry", "fn-return"]
    assert registry.get_matching_breakpoint_ids(
        co_name="add",
        co_qualname="AdditionEngine.add",
        co_filename=str(ADDITION_ENGINE_FILE),
        lineno=5,
        event=TraceEvent.CALL,
    ) == ["fn-entry", "fn-return"]


def test_multiple_method_breakpoints_same_qualname_return_all_ids():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="method-entry",
            type=BreakpointType.METHOD,
            value="AdditionEngine.add",
        )
    )
    registry.register(
        Breakpoint(
            id="method-both",
            type=BreakpointType.METHOD,
            value="AdditionEngine.add",
            capture_mode=CaptureMode.BOTH,
        )
    )

    assert registry.get_method_breakpoint_ids("AdditionEngine.add") == [
        "method-entry",
        "method-both",
    ]


def test_multiple_file_line_breakpoints_same_location_return_all_ids():
    registry = BreakpointRegistry()
    registry.register(
        Breakpoint(
            id="line-entry",
            type=BreakpointType.FILE_LINE,
            file="target/engines/addition.py",
            line=5,
        )
    )
    registry.register(
        Breakpoint(
            id="line-return",
            type=BreakpointType.FILE_LINE,
            file=str(ADDITION_ENGINE_FILE),
            line=5,
            capture_mode=CaptureMode.RETURN,
        )
    )

    ids = registry.get_line_breakpoint_ids(str(ADDITION_ENGINE_FILE), 5)
    assert ids == ["line-entry", "line-return"]
    assert registry.get_matching_breakpoint_ids(
        co_name="add",
        co_qualname="AdditionEngine.add",
        co_filename=str(ADDITION_ENGINE_FILE),
        lineno=5,
        event=TraceEvent.LINE,
    ) == ["line-entry", "line-return"]
