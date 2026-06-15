# Project Context — HyperProbe PoC

Living log of decisions, environment, and progress. **Append brief entries** when something important changes.  
See also: [`CODE_STYLE.md`](CODE_STYLE.md) · local design docs in `notes/` (gitignored)

---

## Repository

| Field | Value |
|-------|--------|
| **GitHub** | https://github.com/Shashank519915/hyperprobe.git |
| **Structure** | Monorepo — `target/` + `agent/` in one repo |
| **Default branch** | `main` |
| **Active branch** | `feat/agent-data-models` (PR-04) |
| **CI workflows** | `ci` (pytest + purity) · `Dependency Graph` (Dependabot — automatic) |

---

## Environment

| Field | Value |
|-------|--------|
| **Python (local)** | 3.12.10 |
| **Python (Docker/CI)** | 3.12 (`python:3.12-slim`) |
| **pytest** | 8.4.2 |
| **OS** | Windows 10/11 (dev) · Linux (CI/Docker) |

---

## Folder layout (local)

```text
hyperprobe/
├── agent/
│   └── models.py       # Breakpoint types (PR-04)
├── target/
│   ├── handlers.py     # layer 1 — RouteHandler
│   ├── server.py       # ThreadingHTTPServer :8080 (PR-03)
│   ├── engines/        # layer 3 — add/sub/mul/div engines
│   └── services/       # layer 2 — MathService
├── tests/
├── scripts/
├── snapshots/
├── notes/              # gitignored — ARCHITECTURE_V2, IMPLEMENTATION_PLAN, DEMO_COMMANDS.md
├── oldnotes/           # gitignored — draft architecture history
├── TASK_CHECKLIST.md   # task tracking (committed)
├── CODE_STYLE.md
├── CONTEXT.md          # this file
└── README.md           # human-written submission doc (later)
```

---

## Key decisions

| Date | Decision |
|------|----------|
| 2026-06-15 | Single repo for target + agent (assignment requirement) |
| 2026-06-15 | Python + `sys.settrace` per `notes/ARCHITECTURE_V2.md` |
| 2026-06-15 | Design docs in `notes/` gitignored; submission README holds 1–2 para architecture |
| 2026-06-15 | Pin runtime to **Python 3.12** (verified locally on 3.12.10) |
| 2026-06-15 | Ports: target `:8080`, agent control `:9090` |
| 2026-06-16 | `notes/DEMO_COMMANDS.md` — single gitignored command/setup reference for human README (not implementation notes) |

---

## Progress log

Append newest entries at the **top**.

### 2026-06-16 — Task 4.2 complete (local)

- Extended `agent/models.py`: TraceEvent, RawFrame, RawCapture, StackFrame, Snapshot
- PR-04 ready — open PR after commit + push

### 2026-06-16 — Task 4.1 committed

- Commit `f3e0deb`: BreakpointType, CaptureMode, Breakpoint; CI green

### 2026-06-16 — Task 4.1 complete (local)

- Added `agent/models.py` — `BreakpointType`, `CaptureMode`, `Breakpoint` (§5.6)
- Restructured `notes/DEMO_COMMANDS.md` as setup/command-only reference
- Next: commit 4.1, then task 4.2 (RawCapture, Snapshot, StackFrame)

### 2026-06-16 — PR-03 merged

- PR #3 merged to `main` (merge `fde52e7`); branch `feat/agent-data-models` from updated `main`
- Target complete: 18 tests, HTTP :8080, purity script

### 2026-06-16 — Task 2.6 complete (local)

- Added `tests/test_target_http.py` — 7 HTTP tests; total 18 pytest cases
- Expanded `scripts/check_target_purity.sh` (trace/logging/agent rules)
- Added `notes/DEMO_COMMANDS.md` — command/output log for human README
- PR-03 ready — open PR after commit + push

### 2026-06-16 — Task 2.5 committed + manual curl verified

- Commit `a220208`: ThreadingHTTPServer on :8080; CI green
- User verified: `python -m target.server` + curl → 200 JSON result 30.0
- PowerShell note: use `curl.exe` or `-UseBasicParsing` (logged in DEMO_COMMANDS.md)

### 2026-06-16 — Task 2.5 complete (local)

- Added `target/server.py` — ThreadingHTTPServer on :8080, `GET /calculate` JSON API
- Three-layer chain complete: handler → service → engine
- Next: commit 2.5, then task 2.6 (HTTP tests + purity script)

### 2026-06-16 — Task 2.4 committed

- Commit `8cafeff`: RouteHandler for /calculate
- CI green on `feat/target-http-server`

### 2026-06-16 — Task 2.4 complete (local)

- Added `target/handlers.py` — `RouteHandler.handle_calculate` (layer 1)
- Parses `op`, `a`, `b` query params; returns `{op, a, b, result}` dict
- Next: commit 2.4, then task 2.5 (ThreadingHTTPServer on :8080)

### 2026-06-16 — PR-02 merged

- PR #2 merged to `main` (merge `c387258`); branch `feat/target-http-server` from updated `main`
- Tasks 2.1–2.3 on `main`: engines, MathService, 11 unit tests

### 2026-06-16 — Task 2.3 complete (local)

- Added `tests/test_target_math.py` — 11 tests (engines + MathService)
- Updated `tests/conftest.py` — repo root on sys.path; removed scaffold hook
- PR-02 ready — open PR after commit + push
- Next: commit 2.3, push, open PR-02

### 2026-06-16 — Task 2.2 committed

- Commit `6fb0c56`: MathService routing to engines
- Pushed to `origin/feat/target-core-layers`

### 2026-06-16 — Task 2.2 complete (local)

- Added `target/services/math_service.py` — `MathService.compute(op, a, b)`
- Routes `add` / `sub` / `mul` / `div` to engines; unknown op → `ValueError`
- Verified task 2.1 push: commit `3d89b08` on `origin/feat/target-core-layers`
- Next: commit 2.2, then task 2.3 (unit tests)

### 2026-06-15 — PR-01 merged; task 2.1 complete (local)

- PR #1 merged to `main` (merge `9c3b6a1`); branched `feat/target-core-layers` from updated `main`
- Task 2.1: four operation engines in `target/engines/` (pure classes, no I/O)
- Next: commit 2.1, then task 2.2 (MathService)

### 2026-06-15 — Task 1.4 complete (local)

- Added `agent/__init__.py`, `target/__init__.py`, `tests/conftest.py`
- `pytest tests/ -q` → 0 tests, exit 0 (conftest scaffold hook)
- Simplified CI pytest step (no exit-5 workaround)
- PR-01 ready — open PR after commit + push
- Next: commit 1.4, push, open PR-01 on GitHub

### 2026-06-15 — Task 1.3 committed

- Commit `f6688e3`: snapshots/.gitkeep + tracking docs + PR workflow docs
- Pushed to `origin/chore/repo-scaffold`

### 2026-06-15 — Task 1.3 complete (local)

- Added `snapshots/.gitkeep` (runtime JSON still gitignored)
- Tracking docs ready to commit: `TASK_CHECKLIST.md`, `CODE_STYLE.md`, `CONTEXT.md`
- Added PR workflow: draft title + detailed description **after last task of each PR** (`CODE_STYLE.md` §7, `IMPLEMENTATION_PLAN.md` §9)
- Next: commit 1.3, then task 1.4

### 2026-06-15 — Task 1.2 complete (pushed, CI green)

- Commit `7256bbb`: CI workflow + purity script stub
- GitHub Actions: `ci` #1 green (27s); `Dependency Graph` green (Dependabot)
- Next: task 1.3

### 2026-06-15 — Task 1.2 complete (local)

- Added `.github/workflows/ci.yml` (Python 3.12, pytest, purity script)
- Added `scripts/check_target_purity.sh` (stub pass until `target/` exists)
- Next: commit 1.2, then task 1.3

### 2026-06-15 — main branch created

- Default branch set to `main` on GitHub (same snapshot as scaffold for now)
- Continue PR-01 work on `chore/repo-scaffold`

### 2026-06-15 — Task 1.1 complete

- Branch: `chore/repo-scaffold`
- Added: `.gitignore`, `requirements.txt`, `requirements-dev.txt`
- Verified: `pip install -r requirements-dev.txt`, `pytest 8.4.2`, `pytest` collects 0 tests
- Pushed to `origin/chore/repo-scaffold`
- Next: task 1.2 (CI + purity script stub)

---

## Git workflow

PR-03 merged to `main`. Current work: **PR-04** on `feat/agent-data-models`.

After each PR merges: `git checkout main` → `git pull origin main` → new feature branch.

---

## Assignment reminders

- README must be **human-written** (no AI-generated prose)
- `target/` must never import `agent/`
- Entrypoint (later): `python -m agent.bootstrap`
