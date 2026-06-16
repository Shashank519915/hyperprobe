"""Tests for target purity enforcement (R3, task 12.2)."""

from pathlib import Path

import pytest

from scripts.target_purity_check import RULES, main, scan_target

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_scan_target_passes_on_real_repo():
    assert scan_target(REPO_ROOT / "target") == []


def test_main_returns_zero_on_real_repo(capsys):
    assert main([]) == 0
    captured = capsys.readouterr()
    assert "check_target_purity: OK" in captured.out


def test_scan_target_fails_when_directory_missing():
    with pytest.raises(FileNotFoundError, match="target/ directory not found"):
        scan_target(REPO_ROOT / "missing-target")


def test_main_fails_when_target_missing(capsys):
    assert main([str(REPO_ROOT / "missing-target")]) == 1
    captured = capsys.readouterr()
    assert "target/ directory not found" in captured.err


@pytest.mark.parametrize(
    ("filename", "content", "needle"),
    [
        ("bad_agent.py", "import agent\n", "must not import agent"),
        ("bad_print.py", "print('hi')\n", "must not use logging or print"),
        (
            "bad_trace.py",
            "import sys\nsys.settrace(None)\n",
            "must not use trace/settrace hooks",
        ),
        (
            "bad_monitor.py",
            "import sys\nsys.monitoring.use_tool_id(0, 0)\n",
            "must not use sys.monitoring",
        ),
        (
            "bad_breakpoint.py",
            "def f():\n    breakpoint()\n",
            "must not call breakpoint()",
        ),
    ],
)
def test_scan_target_detects_violation(
    tmp_path: Path,
    filename: str,
    content: str,
    needle: str,
):
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    target_dir.joinpath(filename).write_text(content, encoding="utf-8")

    violations = scan_target(target_dir)
    assert len(violations) == 1
    assert needle in violations[0]
    assert filename in violations[0]


def test_scan_target_ignores_comment_lines(tmp_path: Path):
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    target_dir.joinpath("ok.py").write_text(
        "# import agent\n# print('hi')\n",
        encoding="utf-8",
    )
    assert scan_target(target_dir) == []


def test_rules_cover_agent_logging_trace_monitoring_breakpoint():
    labels = {label for label, _ in RULES}
    assert "must not import agent" in labels
    assert "must not use sys.monitoring" in labels
    assert "must not call breakpoint()" in labels
