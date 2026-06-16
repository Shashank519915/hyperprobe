"""Scan target/ for forbidden observability hooks (R3)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET_DIR = REPO_ROOT / "target"

RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "must not import agent",
        re.compile(r"(^|\s)import\s+agent|from\s+agent"),
    ),
    (
        "must not use logging or print",
        re.compile(r"^\s*(import logging|from logging|print\()"),
    ),
    (
        "must not use trace/settrace hooks",
        re.compile(
            r"(sys\.settrace|threading\.settrace|import trace|from trace)"
        ),
    ),
    ("must not use sys.monitoring", re.compile(r"sys\.monitoring")),
    (
        "must not use OpenTelemetry or debug/profiling imports",
        re.compile(
            r"(opentelemetry|OpenTelemetry|import pdb|from pdb|"
            r"import cProfile|from cProfile)"
        ),
    ),
    ("must not call breakpoint()", re.compile(r"\sbreakpoint\(")),
)


def scan_target(target_dir: Path) -> list[str]:
    """Return human-readable violation lines (file:lineno: text)."""
    if not target_dir.is_dir():
        raise FileNotFoundError(f"target/ directory not found at {target_dir}")

    violations: list[str] = []
    for path in sorted(target_dir.rglob("*.py")):
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            for label, pattern in RULES:
                if pattern.search(line):
                    rel = path.relative_to(target_dir.parent)
                    violations.append(f"{label}: {rel}:{lineno}: {line.rstrip()}")
                    break
    return violations


def main(argv: list[str] | None = None) -> int:
    target_dir = DEFAULT_TARGET_DIR
    args = list(argv if argv is not None else sys.argv[1:])
    if args:
        target_dir = Path(args[0]).resolve()

    print(f"check_target_purity: scanning {target_dir}")
    try:
        violations = scan_target(target_dir)
    except FileNotFoundError as exc:
        print(f"check_target_purity: FAIL — {exc}", file=sys.stderr)
        return 1

    if violations:
        for item in violations:
            print(f"check_target_purity: {item}", file=sys.stderr)
        print("check_target_purity: FAIL — see violations above", file=sys.stderr)
        return 1

    print("check_target_purity: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
