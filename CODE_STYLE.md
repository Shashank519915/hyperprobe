# Code Style & Engineering Conventions — HyperProbe PoC

Brief rules for this repo. Authoritative design: `notes/ARCHITECTURE_V2.md` (local).  
**Project updates:** append to [`CONTEXT.md`](CONTEXT.md).

---

## 1. Repository layout

| Path | Rule |
|------|------|
| `target/` | Calculator only. **Zero** agent imports, logging, tracing, metrics, prints. |
| `agent/` | Instrumentation only. No calculator business logic. |
| `tests/` | pytest tests mirroring modules. |
| `notes/` | Local design docs (gitignored). |
| `snapshots/` | Runtime JSON output (gitignored except `.gitkeep`). |

**One repo** — do not split target and agent across repositories.

---

## 2. Python version

- **Local dev:** Python 3.12.x
- **Docker / CI:** `python:3.12-slim`, `python-version: "3.12"`
- Use stdlib first; add dependencies only when justified (e.g. PyYAML in PR-05)

---

## 3. Formatting & naming

| Item | Convention |
|------|--------------|
| Style | PEP 8, 4-space indent |
| Modules | `snake_case.py` |
| Classes | `PascalCase` |
| Functions / methods | `snake_case` |
| Constants | `UPPER_SNAKE_CASE` |
| Types | Prefer `dataclass` + `Enum` for models (`agent/models.py`) |

Keep functions small. Match existing patterns in the file you edit.

---

## 4. Target application rules (strict)

Forbidden in `target/`:

- `import agent` or any agent path
- `logging`, `print`, OpenTelemetry, custom trace hooks
- Decorators or wrappers for observability
- Manual snapshot / capture calls

Allowed: stdlib only for HTTP (`http.server`), math, parsing query params.

---

## 5. Agent rules

| Rule | Detail |
|------|--------|
| Hot path | Trace callback: fast reject, sync `RawCapture`, `put_nowait` only |
| Never | Queue `frame` objects; block on I/O in trace callback |
| Errors | `try/except` in trace callback and worker — never crash target |
| Threads | Agent worker/control threads call `sys.settrace(None)` on start |
| Ports | Control API `:9090` only — never on target `:8080` |

---

## 6. Testing style

**Framework:** pytest

| Practice | Detail |
|----------|--------|
| Layout | `tests/test_<area>.py` |
| Naming | `test_<behavior>_<expected>()` |
| Unit vs integration | Unit: no Docker; integration: HTTP + snapshots |
| Target tests | Must not import or start agent |
| Tracer tests | Explicit RETURN / file-line / multi-BP cases per architecture |
| Run | `pytest tests/ -q` before every push |

Example:

```python
def test_addition_engine_returns_sum():
    assert AdditionEngine().add(10, 20) == 30
```

Prefer explicit assertions over broad `assert result` without context.

---

## 7. Git & commits

### Branch flow

1. One branch per PR (see `notes/IMPLEMENTATION_PLAN.md`)
2. One task → one commit (or tight commit group)
3. Merge to `main` in PR order only

### Commit messages

**During planning:** `notes/IMPLEMENTATION_PLAN.md` has short **placeholder** subjects.

**After completing a task:** write a **detailed** commit message that records what actually shipped:

```
chore: add gitignore and Python dependency files for PoC scaffold

- Add .gitignore for venv, pytest cache, snapshots/*.json, notes/, oldnotes/
- Add requirements.txt (stdlib-first, no runtime deps yet)
- Add requirements-dev.txt with pytest>=8,<9
- Verify locally on Python 3.12.10: pip install and pytest --version OK
```

Format:

- **Subject:** imperative, ≤72 chars, conventional prefix (`feat`, `fix`, `test`, `chore`, `docs`)
- **Body:** bullet list of files changed, behavior, verification run

Track final message in `TASK_CHECKLIST.md` → column **Actual commit**.

### Pull requests

**When:** Open a PR only after the **last task** of that PR section is done, committed, and pushed (e.g. open PR-01 after task **1.4**, not after 1.2).

**Who drafts:** After the final task, the assistant (or you) fills **PR title** and **PR description** in `TASK_CHECKLIST.md` under that PR’s **Pull request draft** block. Copy-paste into GitHub when opening the PR.

**Base / compare:** `main` ← feature branch (e.g. `chore/repo-scaffold`).

**Title format:**

```text
<prefix>: <short summary> (PR-NN)
```

Examples: `chore: repo scaffold (PR-01)` · `feat(target): core math layers (PR-02)`

**Description format** (detailed — one subsection per task in the PR):

```markdown
## Summary
One sentence: what this PR delivers and which requirements it advances.

## Tasks included
### Task X.Y — <title>
- **Files:** …
- **Behavior:** …
- **Verification:** …

(repeat for every task in this PR)

## Requirements touched
R… (from IMPLEMENTATION_PLAN matrix)

## Test plan
- [ ] CI green (`ci` workflow)
- [ ] …

## Merge notes
Depends on PR-… · No application logic yet / etc.
```

**GitHub steps:** Push branch → repo **Pull requests** → **New pull request** → base `main`, compare feature branch → paste title + description → **Create pull request** → wait for checks → **Merge** when green.

See `notes/IMPLEMENTATION_PLAN.md` §9 for per-PR draft placeholders.

---

## 8. Documentation

| Doc | Rule |
|-----|------|
| `README.md` | **You write manually** — assignment forbids AI-generated README |
| `notes/ARCHITECTURE_V2.md` | Design reference (local) |
| `TASK_CHECKLIST.md` | Update status after each task |
| `CONTEXT.md` | Append progress / decisions |
| `COMPLIANCE_CHECKLIST.md` | Added in PR-12 |

---

## 9. Dependencies

- Minimize runtime deps
- Dev deps in `requirements-dev.txt` only
- Pin major versions where sensible (`pytest>=8,<9`)
- Document new runtime deps in README when added

---

## 10. Docker (when added)

- Base: `python:3.12-slim`
- Entrypoint: `python -m agent.bootstrap`
- Reviewer flow: `docker compose up --build` only

---

## 11. What not to build

Per architecture §10.2 — do not add:

DELETE/PATCH control API, stats endpoint, retention module, MCP, Redis, Kafka, Next.js, eBPF, bytecode rewriting in PoC.

---

## 12. Cursor workflow

1. Read task in `TASK_CHECKLIST.md`
2. Paste relevant section from `notes/ARCHITECTURE_V2.md`
3. Implement → test → update checklist + `CONTEXT.md`
4. Commit with detailed message → push
5. **After the last task in a PR:** fill **Pull request draft** in `TASK_CHECKLIST.md` (title + detailed description) → open PR on GitHub → merge when CI green

---

*Update this file when team conventions change; log the change in CONTEXT.md.*
