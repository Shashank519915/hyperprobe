from pathlib import Path

from agent.breakpoints import (
    matches_breakpoint,
    matches_file_line_breakpoint,
    matches_function_breakpoint,
    matches_method_breakpoint,
    normalize_path,
)
from agent.models import Breakpoint, BreakpointType, TraceEvent

REPO_ROOT = Path(__file__).resolve().parents[1]
ADDITION_ENGINE_FILE = REPO_ROOT / "target" / "engines" / "addition.py"


def test_normalize_path_resolves_relative_to_absolute():
    rel = REPO_ROOT / "target" / "engines" / "addition.py"
    assert normalize_path("target/engines/addition.py") == normalize_path(rel)


def test_normalize_path_string_and_path_equivalent():
    target_file = REPO_ROOT / "agent" / "models.py"
    assert normalize_path(str(target_file)) == normalize_path(target_file)


def test_normalize_path_collapses_dot_segments():
    messy = REPO_ROOT / "target" / ".." / "target" / "engines" / "addition.py"
    clean = REPO_ROOT / "target" / "engines" / "addition.py"
    assert normalize_path(messy) == normalize_path(clean)


def test_normalize_path_same_file_twice_is_stable():
    target_file = REPO_ROOT / "target" / "handlers.py"
    first = normalize_path(target_file)
    second = normalize_path(target_file)
    assert first == second


def test_function_breakpoint_matches_co_name_on_call():
    bp = Breakpoint(
        id="bp-fn",
        type=BreakpointType.FUNCTION,
        value="add",
    )
    assert matches_function_breakpoint(bp, "add", TraceEvent.CALL)
    assert not matches_function_breakpoint(bp, "add", TraceEvent.LINE)
    assert not matches_function_breakpoint(bp, "subtract", TraceEvent.CALL)


def test_method_breakpoint_matches_co_qualname_exactly():
    bp = Breakpoint(
        id="bp-method",
        type=BreakpointType.METHOD,
        value="AdditionEngine.add",
    )
    assert matches_method_breakpoint(bp, "AdditionEngine.add", TraceEvent.CALL)
    assert not matches_method_breakpoint(bp, "add", TraceEvent.CALL)
    assert not matches_method_breakpoint(bp, "AdditionEngine.add", TraceEvent.RETURN)


def test_file_line_breakpoint_matches_normalized_path_and_line():
    bp = Breakpoint(
        id="bp-line",
        type=BreakpointType.FILE_LINE,
        file="target/engines/addition.py",
        line=5,
    )
    absolute = str(ADDITION_ENGINE_FILE)
    assert matches_file_line_breakpoint(bp, absolute, 5, TraceEvent.LINE)
    assert matches_file_line_breakpoint(
        bp, "target/engines/addition.py", 5, TraceEvent.LINE
    )
    assert not matches_file_line_breakpoint(bp, absolute, 5, TraceEvent.CALL)
    assert not matches_file_line_breakpoint(bp, absolute, 4, TraceEvent.LINE)


def test_matches_breakpoint_dispatches_by_type():
    function_bp = Breakpoint(id="1", type=BreakpointType.FUNCTION, value="compute")
    method_bp = Breakpoint(
        id="2", type=BreakpointType.METHOD, value="MathService.compute"
    )
    line_bp = Breakpoint(
        id="3",
        type=BreakpointType.FILE_LINE,
        file=str(ADDITION_ENGINE_FILE),
        line=5,
    )
    kwargs = {
        "co_name": "compute",
        "co_qualname": "MathService.compute",
        "co_filename": str(ADDITION_ENGINE_FILE),
        "lineno": 5,
        "event": TraceEvent.CALL,
    }
    assert matches_breakpoint(function_bp, **kwargs)
    assert matches_breakpoint(method_bp, **kwargs)

    no_match = {
        **kwargs,
        "co_name": "other",
        "co_qualname": "Other.thing",
    }
    assert not matches_breakpoint(function_bp, **no_match)
    assert not matches_breakpoint(method_bp, **no_match)

    line_kwargs = {**kwargs, "event": TraceEvent.LINE}
    assert matches_breakpoint(line_bp, **line_kwargs)
    assert not matches_breakpoint(function_bp, **line_kwargs)
