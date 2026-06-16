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
| **Active branch** | `feat/agent-tracer` (PR-08) |
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
│   ├── models.py       # Breakpoint + snapshot models (PR-04)
│   ├── breakpoints.py  # normalize_path + matchers + YAML loader
│   ├── registry.py     # BreakpointRegistry
│   ├── serializer.py   # SafeSerializer (PR-06)
│   ├── capture.py      # sync RawCapture from live frames (PR-07)
│   ├── worker.py       # SnapshotWorker + JSON write (PR-07)
│   ├── installer.py    # sys.settrace + threading.settrace (PR-08)
│   └── tracer.py       # global_trace + local trace tiers (PR-08)
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
├── breakpoints.yaml    # seed breakpoint config (PR-05)
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
| 2026-06-16 | `notes/DEMO_COMMANDS.md` — updated after each merged PR / verified milestone (setup + commands only) |

---

## Progress log

Append newest entries at the **top**.

### 2026-06-16 — Task 8.5 complete (local)

- Added `local_trace_combined` dispatcher when method RETURN/BOTH overlaps watched file (§5.3 step 5)
- Added `tests/test_tracer_combined.py` — 3 tests; pytest 100 passed
- Next: commit 8.5, then task 8.6 (agent thread isolation)

### 2026-06-16 — Task 8.4 committed + pushed

- Commit `afeba41` on `feat/agent-tracer`; CI green

### 2026-06-16 — Task 8.4 complete (local)

- Added `local_trace_for_file_line_breakpoint` + `_capture_file_line_hits` (§5.3)
- Added `tests/test_tracer_tiers.py` — 5 tests; pytest 97 passed
- Next: commit 8.4, then task 8.5 (combined local trace)

### 2026-06-16 — Task 8.3 committed + pushed

- Commit `0e05fc3` on `feat/agent-tracer`; CI green

### 2026-06-16 — Task 8.3 complete (local)

- Implemented RETURN/BOTH capture in `local_trace_for_function_breakpoint` (§5.3)
- Added `tests/test_capture_lifetime.py` — 4 tests; updated BOTH/RETURN in `test_tracer_global.py`
- pytest 92 passed
- Next: commit 8.3, then task 8.4 (file_line local trace)

### 2026-06-16 — Task 8.2 committed + pushed

- Commit `13439df` on `feat/agent-tracer`; CI green

### 2026-06-16 — Task 8.2 complete (local)

- Added `agent/tracer.py` — `Tracer.global_trace` with fast reject + ENTRY capture (§5.3)
- Added `tests/test_tracer_global.py` — 8 tests; pytest 88 passed
- Next: commit 8.2, then task 8.3 (local_trace RETURN/BOTH)

### 2026-06-16 — Task 8.1 committed + pushed

- Commit `2bea1ba` on `feat/agent-tracer`; CI green

### 2026-06-16 — Task 8.1 complete (local)

- Added `agent/installer.py` — `TraceInstaller`, `install_trace`, `remove_trace` (R15)
- Added `tests/test_installer.py` — 6 tests; pytest 80 passed
- Next: commit 8.1, then task 8.2 (global_trace)

### 2026-06-16 — PR-07 merged

- PR #7 merged to `main` (merge `03279c0`); CI green
- Capture pipeline on main: capture.py, worker.py, 74 pytest at merge
- Branch `feat/agent-tracer` for PR-08

### 2026-06-16 — Task 6.3 committed + pushed

- Commit `211c9a4`; opened PR #7

### 2026-06-16 — Task 6.3 complete (local)

- Added `create_capture_queue`, `enqueue_capture`, `DropLogger` to `agent/worker.py` (§5.8.1)
- Extended `tests/test_worker.py` — 6 overflow tests (13 total); pytest 74 passed
- PR-07 ready — open PR after commit + push

### 2026-06-16 — Task 6.2 committed + pushed

- Commit `7fb47c6` on `feat/agent-capture-worker`; CI green

### 2026-06-16 — Task 6.2 complete (local)

- Added `agent/worker.py` — `build_snapshot`, `SnapshotWorker`, JSON write to `snapshots/`
- Added `tests/test_worker.py` — 7 tests; pytest 68 passed
- Next: commit 6.2, then task 6.3 (bounded queue overflow)

### 2026-06-16 — Task 6.1 committed + pushed

- Commit `37e7b41` on `feat/agent-capture-worker`; CI green

### 2026-06-16 — Task 6.1 complete (local)

- Added `agent/capture.py` — `capture_stack_frames`, `capture_raw` (§5.5)
- Added `tests/test_capture.py` — 8 tests; nested stack, return via settrace; pytest 61 passed
- Next: commit 6.1, then task 6.2 (SnapshotWorker)

### 2026-06-16 — PR-06 merged

- PR #6 merged to `main` (merge `edfbce1`); CI green
- `SafeSerializer` + 15 pathological tests on main; pytest 53 passed
- Commits: `3517cac` (7.1), `b0390a2` (7.2)
- Paused — resume with PR-07 (`feat/agent-capture-worker`, tasks 6.1–6.3)

### 2026-06-16 — Task 7.2 committed + pushed

- Commit `b0390a2` on `feat/agent-safe-serializer`; opened PR #6

### 2026-06-16 — Task 7.2 complete (local)

- Hardened `agent/serializer.py` — per-item dict/list guards, bad-key fallback
- Extended `tests/test_serializer.py` — 8 pathological cases (15 total); pytest 53 passed

### 2026-06-16 — Task 7.1 committed + pushed

- Commit `3517cac` on `feat/agent-safe-serializer`; CI green
- `SafeSerializer` + 7 baseline tests (45 pytest total)

### 2026-06-16 — Task 7.1 complete (local)

- Added `agent/serializer.py` — SafeSerializer with type fallbacks
- Added `tests/test_serializer.py` — 7 tests; pytest 45 passed
- Updated `notes/DEMO_COMMANDS.md` (PR-05/06 test commands)

### 2026-06-16 — PR-05 merged

- PR #5 merged to `main` (merge `4046196`); branch `feat/agent-safe-serializer`
- Breakpoint registry + `breakpoints.yaml` on main; CI green

### 2026-06-16 — Task 5.5 complete (local)

- Added `breakpoints.yaml` + `load_breakpoints_yaml` / `breakpoint_from_dict`
- Added PyYAML to `requirements.txt`; 38 pytest total
- PR-05 ready — open PR after commit + push

### 2026-06-16 — Task 5.4 committed

- Commit `b7e13d8`: multiple BPs per target; CI green

### 2026-06-16 — Task 5.4 complete (local)

- Added `get_matching_breakpoint_ids` — all matching bp ids, no deduplication
- Tests: multiple function/method/file_line BPs on same target (34 pytest total)
- Next: commit 5.4, then task 5.5 (breakpoints.yaml loader)

### 2026-06-16 — Task 5.3 committed

- Commit `64844b5`: BreakpointRegistry with O(1) indexes

### 2026-06-16 — Task 5.3 complete (local)

- Added `agent/registry.py` — thread-safe BreakpointRegistry with O(1) indexes
- Added `tests/test_registry.py` — 5 tests; pytest 31 passed
- Next: commit 5.3, then task 5.4 (multiple BPs same target)

### 2026-06-16 — Task 5.2 committed

- Commit `1852668`: breakpoint matchers; CI green

### 2026-06-16 — Task 5.2 complete (local)

- Added breakpoint matchers: function, method, file_line + `matches_breakpoint` dispatcher
- Extended `tests/test_breakpoints.py` — 8 tests total; pytest 26 passed
- Next: commit 5.2, then task 5.3 (registry indexes)

### 2026-06-16 — Task 5.1 committed

- Commit `05dcf8e`: `normalize_path`; CI green on push

### 2026-06-16 — Task 5.1 complete (local)

- Added `agent/breakpoints.py` — `normalize_path()` via `Path.resolve()`
- Added `tests/test_breakpoints.py` — 4 path normalization tests (22 total pytest)
- Next: commit 5.1, then task 5.2 (matchers)

### 2026-06-16 — PR-04 merged

- PR #4 merged to `main` (merge `f96581f`); branch `feat/agent-breakpoint-registry`
- Tasks 4.1–4.2: full agent model layer on main; CI green

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

PR-07 merged to `main`. **PR-08** on `feat/agent-tracer` — tasks 8.1–8.5 done locally (8.5 commit pending).

After each PR merges: `git checkout main` → `git pull origin main` → new feature branch.

---

## Assignment reminders

- README must be **human-written** (no AI-generated prose)
- `target/` must never import `agent/`
- Entrypoint (later): `python -m agent.bootstrap`
