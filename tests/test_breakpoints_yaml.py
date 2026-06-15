from pathlib import Path

import pytest

from agent.breakpoints import breakpoint_from_dict, load_breakpoints_yaml
from agent.models import BreakpointType, CaptureMode
from agent.registry import BreakpointRegistry

REPO_ROOT = Path(__file__).resolve().parents[1]
SEED_YAML = REPO_ROOT / "breakpoints.yaml"


def test_load_repo_breakpoints_yaml_registers_all_seed_types():
    registry = BreakpointRegistry()
    loaded = load_breakpoints_yaml(SEED_YAML, registry)

    assert len(loaded) == 3
    assert {bp.type for bp in loaded} == {
        BreakpointType.FUNCTION,
        BreakpointType.METHOD,
        BreakpointType.FILE_LINE,
    }
    assert registry.get("seed-function-compute") is not None
    assert registry.get("seed-method-add") is not None
    assert registry.get("seed-line-addition-return") is not None
    assert registry.get_function_breakpoint_ids("compute") == ["seed-function-compute"]
    assert registry.get_method_breakpoint_ids("AdditionEngine.add") == ["seed-method-add"]


def test_breakpoint_from_dict_assigns_uuid_when_id_missing():
    bp = breakpoint_from_dict(
        {"type": "function", "value": "add", "capture_mode": "ENTRY"}
    )
    assert bp.id
    assert bp.type == BreakpointType.FUNCTION
    assert bp.value == "add"
    assert bp.capture_mode == CaptureMode.ENTRY


def test_breakpoint_from_dict_file_line_requires_file_and_line():
    with pytest.raises(ValueError, match="file and line"):
        breakpoint_from_dict({"type": "file_line", "capture_mode": "ENTRY"})


def test_load_breakpoints_yaml_rejects_empty_file(tmp_path: Path):
    empty = tmp_path / "empty.yaml"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        load_breakpoints_yaml(empty, BreakpointRegistry())
