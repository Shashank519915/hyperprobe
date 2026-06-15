# Task Checklist — HyperProbe PoC

Track every implementation task. Update **Status**, **Actual commit**, and **Verification** as you go.  
Plan reference: `notes/IMPLEMENTATION_PLAN.md` · Design: `notes/ARCHITECTURE_V2.md`

**Status values:** `⬜ todo` · `🔄 in progress` · `✅ done` · `⛔ blocked`

**Commit rule:** Placeholder subjects live in the plan; after each task, write a **detailed** commit message (see `CODE_STYLE.md` §7) and record it here.

---

## Summary

| PR | Branch | Tasks | Done | Status |
|----|--------|-------|------|--------|
| PR-01 | `chore/repo-scaffold` | 1.1–1.4 | 4/4 | ✅ merged |
| PR-02 | `feat/target-core-layers` | 2.1–2.3 | 3/3 | ✅ merged |
| PR-03 | `feat/target-http-server` | 2.4–2.6 | 3/3 | ✅ merged |
| PR-04 | `feat/agent-data-models` | 4.1–4.2 | 2/2 | ✅ merged |
| PR-05 | `feat/agent-breakpoint-registry` | 5.1–5.5 | 4/5 | 🔄 in progress |
| PR-06 | `feat/agent-safe-serializer` | 7.1–7.2 | 0/2 | ⬜ todo |
| PR-07 | `feat/agent-capture-worker` | 6.1–6.3 | 0/3 | ⬜ todo |
| PR-08 | `feat/agent-tracer` | 8.1–8.6 | 0/6 | ⬜ todo |
| PR-09 | `feat/agent-control-api` | 9.1–9.3 | 0/3 | ⬜ todo |
| PR-10 | `feat/agent-bootstrap` | 10.1–10.2 | 0/2 | ⬜ todo |
| PR-11 | `feat/docker` | 11.1–11.3 | 0/3 | ⬜ todo |
| PR-12 | `test/integration-compliance` | 11.4–11.8, 12.1 | 0/6 | ⬜ todo |
| PR-13 | `chore/ci-hardening` | 12.2–12.3 | 0/2 | ⬜ todo |
| PR-14 | `docs/readme` | 14.1 | 0/1 | ⬜ todo |

---

## PR-01 — `chore/repo-scaffold`

### Task 1.1 — Gitignore and Python dependencies

| Field | Detail |
|-------|--------|
| **Status** | ✅ done |
| **Branch** | `chore/repo-scaffold` |
| **Requirements** | R34 prep |
| **Files** | `.gitignore`, `requirements.txt`, `requirements-dev.txt` |
| **Done when** | `pip install -r requirements-dev.txt` works; pytest runs |

**Delivered:**

- `.gitignore` — Python, venv, pytest cache, `snapshots/*.json`, `.env`, `/notes`, `/oldnotes`
- `requirements.txt` — empty/minimal (stdlib-first)
- `requirements-dev.txt` — `pytest>=8,<9`

**Verification:**

```text
Python 3.12.10
pip install -r requirements-dev.txt → OK (pytest 8.4.2)
pytest → collected 0 items, exit 0
```

**Placeholder commit (plan):** `chore: add gitignore and Python dependency files`

**Actual commit hash:** `63e990e` (or run `git log -1 --oneline` on branch after 1.1)

**Actual commit message:**

```text
(fill after completion — detailed body per CODE_STYLE.md)
Example:
chore: add gitignore and Python dependency files for PoC scaffold

- Ignore venv, pytest cache, snapshot JSON output, notes/, oldnotes/
- Add requirements.txt (stdlib-first, no runtime deps yet)
- Add requirements-dev.txt with pytest>=8,<9
- Verified on Python 3.12.10: pip install and pytest run OK
```

**Notes:** Pushed to https://github.com/Shashank519915/hyperprobe.git

---

### Task 1.2 — CI workflow and purity script stub

| Field | Detail |
|-------|--------|
| **Status** | ✅ done |
| **Branch** | `chore/repo-scaffold` |
| **Requirements** | R34 prep |
| **Files** | `.github/workflows/ci.yml`, `scripts/check_target_purity.sh` |
| **Done when** | CI runs on push; purity script exits 0 (stub) |

**Delivered:**

- `.github/workflows/ci.yml` — Python 3.12, pytest, purity script on PR/push
- `scripts/check_target_purity.sh` — stub pass if `target/` missing; basic grep rules when present

**Verification:**

```text
GitHub Actions — ci #1 (7256bbb): green, 27s, branch chore/repo-scaffold
GitHub Actions — Dependency Graph: green (Dependabot, automatic)
pytest tests/ -q → 0 tests collected, exit 0 (CI treats exit 5 as OK until 1.4)
bash scripts/check_target_purity.sh → stub pass (CI/Linux; optional locally on Windows)
```

**Placeholder commit:** `chore: add CI workflow for pytest and purity stub`

**Actual commit hash:** `7256bbb`

**Actual commit message:**

```text
chore: add CI workflow and target purity script stub

- Add .github/workflows/ci.yml (Python 3.12, pytest, check_target_purity.sh)
- Trigger on push to main, chore/repo-scaffold, feat/**, test/** and on PRs
- Add scripts/check_target_purity.sh stub (passes when target/ absent)
- pytest allows empty tests/ until task 1.4 adds conftest
```

**Notes:** Pushed to `origin/chore/repo-scaffold`. Two workflows visible in Actions: `ci` (ours) and `Dependency Graph` (GitHub/Dependabot — automatic, both green).

---

### Task 1.3 — Snapshots dir and repo hygiene

| Field | Detail |
|-------|--------|
| **Status** | ✅ done |
| **Branch** | `chore/repo-scaffold` |
| **Requirements** | R11 prep |
| **Files** | `snapshots/.gitkeep`, `TASK_CHECKLIST.md`, `CODE_STYLE.md`, `CONTEXT.md` |
| **Done when** | Tracking docs in repo root; design docs remain in gitignored `notes/` |

**Delivered:**

- `snapshots/.gitkeep` — keeps output dir in repo; `snapshots/*.json` gitignored
- `TASK_CHECKLIST.md`, `CODE_STYLE.md`, `CONTEXT.md` — committed tracking docs
- `CODE_STYLE.md` §7 — PR title/description rule (draft after last task in each PR)
- `notes/IMPLEMENTATION_PLAN.md` §9 — PR-01 draft template (local, gitignored)

**Note:** `ARCHITECTURE_V2.md` / `IMPLEMENTATION_PLAN.md` live in `notes/` (local only). Submission uses human-written `README.md` for architecture summary.

**Placeholder commit:** `chore: add snapshots dir and project tracking docs`

**Actual commit hash:** `f6688e3`

**Actual commit message:**

```text
chore: add snapshots dir and project tracking docs

- Add snapshots/.gitkeep (runtime JSON remains gitignored)
- Add TASK_CHECKLIST.md, CODE_STYLE.md, CONTEXT.md for progress tracking
- Document PR draft workflow: title + detailed description after last task per PR
- Update checklist: task 1.2 CI verified green (ci + Dependency Graph)
```

**Verification:**

```text
snapshots/.gitkeep exists
.gitignore allows !snapshots/.gitkeep while ignoring snapshots/*.json
CODE_STYLE.md documents PR draft workflow (§7)
Pushed to origin/chore/repo-scaffold
```

**Notes:**

---

### Task 1.4 — Package init files

| Field | Detail |
|-------|--------|
| **Status** | ✅ done |
| **Branch** | `chore/repo-scaffold` |
| **Requirements** | — |
| **Files** | `agent/__init__.py`, `target/__init__.py`, `tests/conftest.py`, `.github/workflows/ci.yml` |
| **Done when** | `pytest tests/ -q` collects 0 tests, exit 0 |

**Delivered:**

- `agent/__init__.py`, `target/__init__.py` — empty packages with module docstrings
- `tests/conftest.py` — scaffold hook so 0 tests exits 0 (not pytest code 5)
- `.github/workflows/ci.yml` — simplified pytest step (no exit-5 workaround)

**Placeholder commit:** `chore: add empty package init files`

**Actual commit hash:** `732ffdd` (merged via PR #1)

**Actual commit message:**

```text
chore: add empty package init files

- Add agent/__init__.py and target/__init__.py (scaffold packages)
- Add tests/conftest.py with scaffold hook for 0 tests, exit 0
- Simplify CI pytest step now that conftest handles empty collection
- Update TASK_CHECKLIST and CONTEXT: PR-01 complete, PR draft ready
```

**Verification:**

```text
pytest tests/ -q → no tests ran, exit 0 (Python 3.12.10, pytest 8.4.2)
```

**Notes:**

---

**PR-01 merge checklist:**

- [x] All tasks 1.1–1.4 ✅
- [x] CI green on PR
- [x] PR merged to `main` (PR #1, merge `9c3b6a1`)

**Pull request draft** *(copy to GitHub after task 1.4 push):*

| Field | Value |
|-------|--------|
| **When** | Now — after task 1.4 commit + push |
| **Base ← Compare** | `main` ← `chore/repo-scaffold` |
| **Title** | `chore: repo scaffold (PR-01)` |

**Description** (paste into GitHub PR body):

```markdown
## Summary
Initial monorepo scaffold: dependencies, CI, tracking docs, empty packages — no calculator or agent logic yet.

## Tasks included

### Task 1.1 — Gitignore and Python dependencies
- **Files:** `.gitignore`, `requirements.txt`, `requirements-dev.txt`
- **Behavior:** Stdlib-first runtime deps; pytest 8.x for dev; ignore venv, snapshots JSON, local `notes/`
- **Verification:** `pip install -r requirements-dev.txt`; Python 3.12.x

### Task 1.2 — CI workflow and purity script stub
- **Files:** `.github/workflows/ci.yml`, `scripts/check_target_purity.sh`
- **Behavior:** GitHub Actions on push/PR (Python 3.12, pytest, purity script); stub passes when `target/` absent
- **Verification:** Actions tab — `ci` workflow green

### Task 1.3 — Snapshots dir and repo hygiene
- **Files:** `snapshots/.gitkeep`, `TASK_CHECKLIST.md`, `CODE_STYLE.md`, `CONTEXT.md`
- **Behavior:** Runtime snapshot JSON gitignored; tracking docs committed; design docs stay in gitignored `notes/`
- **Verification:** `snapshots/` exists; docs in repo root

### Task 1.4 — Package init files
- **Files:** `agent/__init__.py`, `target/__init__.py`, `tests/conftest.py`
- **Behavior:** Empty packages for later code; pytest collects 0 tests, exit 0
- **Verification:** `pytest tests/ -q`

## Requirements touched
R11 prep (snapshots dir) · R34 prep (scaffold / CI foundation)

## Test plan
- [ ] `ci` workflow green on this branch
- [ ] `pytest tests/ -q` — 0 tests, exit 0
- [ ] `bash scripts/check_target_purity.sh` — stub pass

## Merge notes
First PR — no merge dependency. After merge, branch `feat/target-core-layers` from updated `main`.
```

---

## PR-02 — `feat/target-core-layers`

### Task 2.1 — Operation engines

| Field | Detail |
|-------|--------|
| **Status** | ✅ done |
| **Branch** | `feat/target-core-layers` |
| **Requirements** | R2, R3, R14 |
| **Files** | `target/engines/addition.py`, `subtraction.py`, `multiplication.py`, `division.py` |
| **Done when** | Pure engine logic; no I/O; no agent imports |

**Delivered:**

- `AdditionEngine.add(a, b)` — addition
- `SubtractionEngine.subtract(a, b)` — subtraction
- `MultiplicationEngine.multiply(a, b)` — multiplication
- `DivisionEngine.divide(a, b)` — division (raises `ZeroDivisionError` when `b == 0`)

**Verification:**

```text
python -c "from target.engines...; assert AdditionEngine().add(10, 20) == 30; ..." → OK
pytest tests/ -q → no tests ran, exit 0
No agent imports, logging, or print in target/engines/
Pushed to origin/feat/target-core-layers (commit 3d89b08)
```

**Placeholder commit:** `feat(target): add operation engines (add/sub/mul/div)`

**Actual commit hash:** `3d89b08`

**Actual commit message:**

```text
feat(target): add operation engines (add/sub/mul/div)

- Add AdditionEngine, SubtractionEngine, MultiplicationEngine, DivisionEngine
- Pure layer-3 math; no I/O, logging, or agent imports
- Update TASK_CHECKLIST and CONTEXT: PR-01 merged, PR-02 task 2.1 done
```

**Notes:** Method qualnames (e.g. `AdditionEngine.add`) align with architecture breakpoint examples. Branch on remote: `feat/target-core-layers` (not `feat/core-target-layers`).

---

### Task 2.2 — MathService

| Field | Detail |
|-------|--------|
| **Status** | ✅ done |
| **Branch** | `feat/target-core-layers` |
| **Requirements** | R2 |
| **Files** | `target/services/math_service.py` |
| **Done when** | `MathService.compute(op, a, b)` routes to engines |

**Delivered:**

- `MathService.compute(op, a, b)` — routes `add` / `sub` / `mul` / `div` to layer-3 engines
- Unknown `op` raises `ValueError` (handler maps to HTTP 400 in task 2.4)
- `ZeroDivisionError` propagates from `DivisionEngine` unchanged

**Verification:**

```text
MathService().compute('add', 10, 20) == 30
MathService().compute('sub'|'mul'|'div', ...) → OK
pytest tests/ -q → no tests ran, exit 0 (before 2.3)
Pushed to origin/feat/target-core-layers
```

**Placeholder commit:** `feat(target): add MathService routing to engines`

**Actual commit hash:** `6fb0c56`

**Actual commit message:**

```text
feat(target): add MathService routing to engines

- Add MathService.compute(op, a, b) routing add/sub/mul/div to layer-3 engines
- Raise ValueError for unsupported op (HTTP mapping in task 2.4)
- Update TASK_CHECKLIST and CONTEXT: task 2.1 verified on remote, 2.2 done
```

**Notes:**

---

### Task 2.3 — Unit tests (math layers)

| Field | Detail |
|-------|--------|
| **Status** | ✅ done |
| **Branch** | `feat/target-core-layers` |
| **Requirements** | R2 |
| **Files** | `tests/test_target_math.py`, `tests/conftest.py` |
| **Done when** | pytest passes |

**Delivered:**

- `tests/test_target_math.py` — 11 tests covering all four engines and MathService routing
- Cases: happy path per op, unknown op → `ValueError`, divide by zero → `ZeroDivisionError`
- `tests/conftest.py` — repo root on `sys.path`; removed scaffold exit-5 hook

**Verification:**

```text
pytest tests/ -q → 11 passed
No agent imports in tests/test_target_math.py
Pushed to origin/feat/target-core-layers
```

**Placeholder commit:** `test(target): unit test MathService and engines`

**Actual commit hash:** `086bed6` (merged via PR #2)

**Actual commit message:**

```text
test(target): unit test MathService and engines

- Add tests/test_target_math.py with 11 cases for engines and MathService
- Update conftest.py: repo root on sys.path for target imports
- Remove scaffold exit-5 hook now that tests exist
- Update TASK_CHECKLIST and CONTEXT: PR-02 ready, PR draft included
```

**Notes:**

---

**PR-02 merge checklist:**

- [x] All tasks 2.1–2.3 ✅
- [x] CI green on PR
- [x] PR merged to `main` (PR #2, merge `c387258`)

**Pull request draft** *(copy to GitHub after task 2.3 push):*

| Field | Value |
|-------|--------|
| **When** | Now — after task 2.3 commit + push |
| **Base ← Compare** | `main` ← `feat/target-core-layers` |
| **Title** | `feat(target): core math layers (PR-02)` |

**Description** (paste into GitHub PR body):

```markdown
## Summary
Layer 2 (MathService) and layer 3 (operation engines) for the calculator target — no HTTP yet, no agent.

## Tasks included

### Task 2.1 — Operation engines
- **Files:** `target/engines/addition.py`, `subtraction.py`, `multiplication.py`, `division.py`
- **Behavior:** One engine class per operation (`AdditionEngine.add`, etc.)
- **Verification:** Pure logic; no I/O, logging, or agent imports

### Task 2.2 — MathService
- **Files:** `target/services/math_service.py`
- **Behavior:** `MathService.compute(op, a, b)` routes `add`/`sub`/`mul`/`div`; unknown op → `ValueError`
- **Verification:** Smoke test; division by zero propagates

### Task 2.3 — Unit tests
- **Files:** `tests/test_target_math.py`, `tests/conftest.py`
- **Behavior:** 11 pytest cases for engines + service routing
- **Verification:** `pytest tests/ -q` — 11 passed

## Requirements touched
R2 (partial — service + engine layers) · R3 · R14

## Test plan
- [ ] `ci` workflow green
- [ ] `pytest tests/ -q` — 11 passed
- [ ] `bash scripts/check_target_purity.sh` — no agent/logging/print in target/

## Merge notes
Depends on PR-01 merged. After merge, branch `feat/target-http-server` from updated `main`.
```

---

## PR-03 — `feat/target-http-server`

### Task 2.4 — RouteHandler

| Field | Detail |
|-------|--------|
| **Status** | ✅ done |
| **Branch** | `feat/target-http-server` |
| **Requirements** | R1, R2 |
| **Files** | `target/handlers.py` |
| **Done when** | Parses query, calls MathService, returns result dict |

**Delivered:**

- `RouteHandler.handle_calculate(query_string)` → `{"op", "a", "b", "result"}`
- `RouteHandler.parse_calculate_query` — extracts `op`, `a`, `b`; missing/invalid params → `ValueError`
- `ValueError` / `ZeroDivisionError` propagate for HTTP mapping in task 2.5

**Verification:**

```text
RouteHandler().handle_calculate('op=add&a=10&b=20') → result 30.0
pytest tests/ -q → 11 passed
Pushed to origin/feat/target-http-server
```

**Placeholder commit:** `feat(target): add RouteHandler for /calculate`

**Actual commit hash:** `8cafeff`

**Actual commit message:**

```text
feat(target): add RouteHandler for /calculate

- Add RouteHandler.handle_calculate parsing op/a/b query params
- Delegate to MathService; return op/a/b/result dict
- Raise ValueError for missing or invalid parameters
- Update TASK_CHECKLIST and CONTEXT: PR-02 merged, PR-03 task 2.4 done
```

**Notes:** CI green on push.

---

### Task 2.5 — ThreadingHTTPServer

| Field | Detail |
|-------|--------|
| **Status** | ✅ done |
| **Branch** | `feat/target-http-server` |
| **Requirements** | R1, R2, R3 |
| **Files** | `target/server.py` |
| **Done when** | `GET /calculate?op=add&a=10&b=20` → JSON on :8080 |

**Delivered:**

- `target/server.py` — stdlib `ThreadingHTTPServer` on `0.0.0.0:8080`
- `GET /calculate` → JSON 200; bad params/op → 400; unknown path → 404
- `create_server()` / `run_server()` for bootstrap import; `if __name__` for dev
- `log_message` suppressed (no stderr access logs)

**Verification:**

```text
Manual: python -m target.server + curl → 200 {"op":"add","a":10.0,"b":20.0,"result":30.0}
HTTP smoke test on ephemeral port — add/div/0/404 OK
pytest tests/ -q → 11 passed (before 2.6)
Pushed to origin/feat/target-http-server; CI green
```

**Placeholder commit:** `feat(target): add ThreadingHTTPServer on :8080`

**Actual commit hash:** `a220208`

**Actual commit message:**

```text
feat(target): add ThreadingHTTPServer on :8080

- Add target/server.py with GET /calculate JSON endpoint
- Wire RouteHandler; map ValueError and ZeroDivisionError to 400
- Export create_server/run_server for bootstrap; dev entry via python -m
- Suppress BaseHTTPRequestHandler access logs (zero observability)
- Update TASK_CHECKLIST and CONTEXT: task 2.4 committed, 2.5 done
```

**Notes:** PowerShell `curl` is `Invoke-WebRequest` — use `curl.exe` or `-UseBasicParsing` in README (see `notes/DEMO_COMMANDS.md`).

---

### Task 2.6 — HTTP tests + purity script update

| Field | Detail |
|-------|--------|
| **Status** | ✅ done |
| **Branch** | `feat/target-http-server` |
| **Requirements** | R1, R3 |
| **Files** | `tests/test_target_http.py`, `scripts/check_target_purity.sh` |
| **Done when** | pytest passes; purity script passes |

**Delivered:**

- `tests/test_target_http.py` — 7 HTTP integration tests (no agent, ephemeral port)
- Covers: add/sub/mul/div, 400 errors, 404, no agent imports in `target/`
- `scripts/check_target_purity.sh` — expanded: agent, logging, print, trace/settrace/opentelemetry
- `notes/DEMO_COMMANDS.md` — local setup/command reference for human README (gitignored)

**Verification:**

```text
pytest tests/ -q → 18 passed
bash scripts/check_target_purity.sh → OK (CI/Linux)
Merged via PR #3; CI green
```

**Placeholder commit:** `test(target): HTTP integration test without agent`

**Actual commit hash:** `2b025a9` (merged via PR #3, merge `fde52e7`)

**Actual commit message:**

```text
test(target): HTTP integration test without agent

- Add tests/test_target_http.py with 7 HTTP integration cases
- Expand check_target_purity.sh for trace/settrace/opentelemetry hooks
- Update TASK_CHECKLIST and CONTEXT: PR-03 complete, PR draft ready
```

**Notes:**

---

**PR-03 merge checklist:**

- [x] All tasks 2.4–2.6 ✅
- [x] CI green on PR
- [x] PR merged to `main` (PR #3, merge `fde52e7`)

**Pull request draft** *(copy to GitHub after task 2.6 push):*

| Field | Value |
|-------|--------|
| **When** | Now — after task 2.6 commit + push |
| **Base ← Compare** | `main` ← `feat/target-http-server` |
| **Title** | `feat(target): HTTP calculator server (PR-03)` |

**Description** (paste into GitHub PR body):

```markdown
## Summary
Complete pristine calculator target: 3-layer stack + HTTP server on :8080. No agent code.

## Tasks included

### Task 2.4 — RouteHandler
- **Files:** `target/handlers.py`
- **Behavior:** Parse `op`/`a`/`b` query; delegate to MathService; return result dict
- **Verification:** Unit smoke test

### Task 2.5 — ThreadingHTTPServer
- **Files:** `target/server.py`
- **Behavior:** `GET /calculate` JSON on :8080; 400/404 error handling; no access logs
- **Verification:** `python -m target.server` + curl

### Task 2.6 — HTTP tests + purity
- **Files:** `tests/test_target_http.py`, `scripts/check_target_purity.sh`
- **Behavior:** 7 HTTP integration tests; stricter purity grep rules
- **Verification:** `pytest tests/ -q` — 18 passed; purity script OK

## Requirements touched
R1 · R2 · R3 · R14

## Test plan
- [ ] `ci` workflow green
- [ ] `pytest tests/ -q` — 18 passed
- [ ] `bash scripts/check_target_purity.sh` — OK

## Merge notes
Depends on PR-02 merged. After merge, can start PR-04 (`feat/agent-data-models`) in parallel with agent work.
```

---

## PR-04 — `feat/agent-data-models`

### Task 4.1 — Breakpoint models

| Field | Detail |
|-------|--------|
| **Status** | ✅ done |
| **Branch** | `feat/agent-data-models` |
| **Requirements** | R10, R16 |
| **Files** | `agent/models.py` |
| **Done when** | Matches ARCHITECTURE_V2 §5.6 |

**Delivered:**

- `BreakpointType` — `function`, `method`, `file_line`
- `CaptureMode` — `ENTRY`, `RETURN`, `BOTH`
- `Breakpoint` dataclass — `id`, `type`, `capture_mode`, `value`, `file`, `line`
- No `enabled` field; file_line uses `file`+`line` (not `value`)

**Verification:**

```text
pytest tests/ -q → 18 passed
Pushed to origin/feat/agent-data-models; CI green
```

**Placeholder commit:** `feat(agent): add Breakpoint and CaptureMode models`

**Actual commit hash:** `f3e0deb`

**Actual commit message:**

```text
feat(agent): add Breakpoint and CaptureMode models

- Add BreakpointType, CaptureMode enums and Breakpoint dataclass
- Match ARCHITECTURE_V2 section 5.6 (function/method/file_line fields)
- Update TASK_CHECKLIST and CONTEXT: PR-03 merged, PR-04 task 4.1 done
```

**Notes:** No imports from `target/` in agent models.

---

### Task 4.2 — RawCapture and Snapshot models

| Field | Detail |
|-------|--------|
| **Status** | ✅ done |
| **Branch** | `feat/agent-data-models` |
| **Requirements** | R10, R20 |
| **Files** | `agent/models.py` |
| **Done when** | Matches ARCHITECTURE_V2 §5.5 / §5.7 |

**Delivered:**

- `TraceEvent` — `call`, `return`, `line`
- `RawFrame` / `RawCapture` — frozen sync copies from trace callback (§5.5)
- `StackFrame` / `Snapshot` — worker output schema with `breakpoint_id`, optional `return_value` (§5.7)

**Verification:**

```text
Import smoke test for RawCapture, RawFrame, Snapshot, StackFrame
pytest tests/ -q → 18 passed
Merged via PR #4 (merge f96581f); CI green
```

**Placeholder commit:** `feat(agent): add RawCapture, Snapshot, StackFrame models`

**Actual commit hash:** `a19020a`

**Actual commit message:**

```text
feat(agent): add RawCapture, Snapshot, StackFrame models

- Add TraceEvent, RawFrame, RawCapture (immutable sync copies, section 5.5)
- Add StackFrame and Snapshot for worker JSON output (section 5.7)
- Update TASK_CHECKLIST and CONTEXT: PR-04 complete, PR draft ready
```

**Notes:**

---

**PR-04 merge checklist:**

- [x] All tasks 4.1–4.2 ✅
- [x] CI green on PR
- [x] PR merged to `main` (PR #4, merge `f96581f`)

**Pull request draft** *(copy to GitHub after task 4.2 push):*

| Field | Value |
|-------|--------|
| **When** | Now — after task 4.2 commit + push |
| **Base ← Compare** | `main` ← `feat/agent-data-models` |
| **Title** | `feat(agent): data models (PR-04)` |

**Description** (paste into GitHub PR body):

```markdown
## Summary
Agent dataclasses for breakpoints, sync capture copies, and snapshot JSON schema — no runtime hooks yet.

## Tasks included

### Task 4.1 — Breakpoint models
- **Files:** `agent/models.py`
- **Behavior:** BreakpointType, CaptureMode, Breakpoint (§5.6)
- **Verification:** No target imports; CI green

### Task 4.2 — RawCapture and Snapshot models
- **Files:** `agent/models.py`
- **Behavior:** TraceEvent, RawFrame, RawCapture (§5.5), StackFrame, Snapshot (§5.7)
- **Verification:** Import smoke test; pytest 18 passed

## Requirements touched
R10 · R16 · R20 (breakpoint_id on snapshot)

## Test plan
- [ ] `ci` workflow green
- [ ] `pytest tests/ -q` — 18 passed

## Merge notes
Depends on PR-01/PR-03 on main. Enables PR-05 (registry) and PR-06/07 (serializer, worker).
```

---

## PR-05 — `feat/agent-breakpoint-registry`

### Task 5.1 — Path normalization

| Field | Detail |
|-------|--------|
| **Status** | ✅ done |
| **Branch** | `feat/agent-breakpoint-registry` |
| **Requirements** | R22 |
| **Files** | `agent/breakpoints.py`, `tests/test_breakpoints.py` |
| **Done when** | `normalize_path()` via `Path.resolve()`; unit tests pass |

**Delivered:**

- `normalize_path(path)` → canonical absolute path string for file_line matching
- `tests/test_breakpoints.py` — 4 path normalization cases (relative, string/path, dot segments, stability)

**Verification:**

```text
pytest tests/test_breakpoints.py -q → 4 passed
pytest tests/ -q → 22 passed
Pushed to origin/feat/agent-breakpoint-registry; CI green
```

**Placeholder commit:** `feat(agent): add path normalization helper`

**Actual commit hash:** `05dcf8e`

**Actual commit message:**

```text
feat(agent): add path normalization helper

- Add agent/breakpoints.py with normalize_path via Path.resolve()
- Add tests/test_breakpoints.py with 4 path normalization cases
- Update TASK_CHECKLIST and CONTEXT: PR-04 merged, PR-05 task 5.1 done
```

**Notes:**

---

### Task 5.2 — Breakpoint matchers

| Field | Detail |
|-------|--------|
| **Status** | ✅ done |
| **Branch** | `feat/agent-breakpoint-registry` |
| **Requirements** | R5, R6, R7 |
| **Files** | `agent/breakpoints.py`, `tests/test_breakpoints.py` |
| **Done when** | function=`co_name`, method=`co_qualname`, file_line=`file`+`line` |

**Delivered:**

- `matches_function_breakpoint` — `co_name` on `call`
- `matches_method_breakpoint` — exact `co_qualname` on `call`
- `matches_file_line_breakpoint` — normalized `file` + `line` on `line`
- `matches_breakpoint` — dispatches by `Breakpoint.type`

**Verification:**

```text
pytest tests/test_breakpoints.py -q → 8 passed
pytest tests/ -q → 26 passed
Pushed to origin/feat/agent-breakpoint-registry; CI green
```

**Placeholder commit:** `feat(agent): add breakpoint matchers`

**Actual commit hash:** `1852668`

**Actual commit message:**

```text
feat(agent): add breakpoint matchers

- Add function/method/file_line matchers and matches_breakpoint dispatcher
- function: co_name on call; method: exact co_qualname; file_line: normalized path + line
- Extend tests/test_breakpoints.py with 4 matcher tests (26 total pytest)
- Update TASK_CHECKLIST and CONTEXT: task 5.1 committed, 5.2 done
```

**Notes:**

---

### Task 5.3 — BreakpointRegistry indexes

| Field | Detail |
|-------|--------|
| **Status** | ✅ done |
| **Branch** | `feat/agent-breakpoint-registry` |
| **Requirements** | R21 |
| **Files** | `agent/registry.py`, `tests/test_registry.py` |
| **Done when** | O(1) indexes per §5.6; thread-safe register |

**Delivered:**

- `BreakpointRegistry` — `threading.RLock`, `register`, `get`, `list_all`
- Indexes: `function_names`, `method_qualnames`, `watched_files`, `*_bps_by_*` dicts
- Lookup helpers: `get_function/method/line_breakpoint_ids`, `has_any_function_or_method_bp`
- Upsert by `id` rebuilds indexes on each register

**Verification:**

```text
pytest tests/test_registry.py -q → 5 passed
pytest tests/ -q → 31 passed
Pushed to origin/feat/agent-breakpoint-registry
```

**Placeholder commit:** `feat(agent): add BreakpointRegistry with O(1) indexes`

**Actual commit hash:** `64844b5`

**Actual commit message:**

```text
feat(agent): add BreakpointRegistry with O(1) indexes

- Add thread-safe BreakpointRegistry with register/get and index rebuild
- O(1) sets and dicts for function, method, and file_line lookups
- Add tests/test_registry.py with 5 registry tests (31 total pytest)
- Update TASK_CHECKLIST and CONTEXT: task 5.2 committed, 5.3 done
```

**Notes:**

---

### Task 5.4 — Multiple breakpoints per target

| Field | Detail |
|-------|--------|
| **Status** | ✅ done (commit pending) |
| **Branch** | `feat/agent-breakpoint-registry` |
| **Requirements** | R20 |
| **Files** | `agent/registry.py`, `tests/test_registry.py` |
| **Done when** | Same name/line → list of bp_ids; no deduplication |

**Delivered:**

- `get_matching_breakpoint_ids(...)` — returns all ids for call/line events (§5.3.1)
- Multiple function BPs sharing `co_name` → distinct ids in registration order
- Same for method qualname and file_line location

**Verification:**

```text
pytest tests/test_registry.py -q → 8 passed
pytest tests/ -q → 34 passed
```

**Placeholder commit:** `feat(agent): support multiple BPs per name/line`

**Actual commit hash:**

**Actual commit message:**

**Notes:**

---

| Task | Status | Files | Req |
|------|--------|-------|-----|
| **5.5** breakpoints.yaml | ⬜ | `breakpoints.yaml` | R29 |

_Record commit hash / message / verification per task when done._

**PR-05 merge checklist:**

- [ ] All tasks 5.1–5.5 ✅
- [ ] CI green on PR
- [ ] PR merged to `main`

**Pull request draft** *(fill after task 5.5 — then open PR on GitHub):*

| Field | Value |
|-------|--------|
| **When** | After task **5.5** is committed and pushed |
| **Base ← Compare** | `main` ← `feat/agent-breakpoint-registry` |
| **Title** | `feat(agent): breakpoint registry (PR-05)` |

---

## PR-06 — `feat/agent-safe-serializer`

| Task | Status | Files | Req |
|------|--------|-------|-----|
| **7.1** SafeSerializer | ⬜ | `agent/serializer.py`, `tests/test_serializer.py` | R30 |
| **7.2** pathological inputs | ⬜ | tests | R31 |

---

## PR-07 — `feat/agent-capture-worker`

| Task | Status | Files | Req |
|------|--------|-------|-----|
| **6.1** sync RawCapture | ⬜ | `agent/capture.py` | R8, R9, R19 |
| **6.2** SnapshotWorker | ⬜ | `agent/worker.py` | R11, R12 |
| **6.3** queue overflow | ⬜ | `agent/worker.py` | R23 |

---

## PR-08 — `feat/agent-tracer` ⚠️ critical path

| Task | Status | Files | Req |
|------|--------|-------|-----|
| **8.1** installer | ⬜ | `agent/installer.py` | R15 |
| **8.2** global_trace | ⬜ | `agent/tracer.py` | R4, R8, R13 |
| **8.3** local_trace function | ⬜ | `agent/tracer.py` | R16, R19 |
| **8.4** local_trace file_line | ⬜ | `agent/tracer.py` | R7, R17 |
| **8.5** combined local trace | ⬜ | `agent/tracer.py` | R18 |
| **8.6** agent thread isolation | ⬜ | worker, control_server | R24 |

---

## PR-09 — `feat/agent-control-api`

| Task | Status | Files | Req |
|------|--------|-------|-----|
| **9.1** control server :9090 | ⬜ | `agent/control_server.py` | R25 |
| **9.2** POST/GET + validation | ⬜ | `agent/control_server.py` | R25–R28 |
| **9.3** dynamic registration test | ⬜ | `tests/test_control_api.py` | R25 |

---

## PR-10 — `feat/agent-bootstrap`

| Task | Status | Files | Req |
|------|--------|-------|-----|
| **10.1** bootstrap entrypoint | ⬜ | `agent/bootstrap.py` | R4, R24, R29 |
| **10.2** smoke test | ⬜ | tests | R1, R11 |

---

## PR-11 — `feat/docker`

| Task | Status | Files | Req |
|------|--------|-------|-----|
| **11.1** Dockerfile | ⬜ | `Dockerfile` (python:3.12-slim) | R32 |
| **11.2** docker-compose | ⬜ | `docker-compose.yml` | R32 |
| **11.3** demo verified | ⬜ | PR description | R32 |

---

## PR-12 — `test/integration-compliance`

| Task | Status | Files | Req |
|------|--------|-------|-----|
| **11.4** RETURN/BOTH tests | ⬜ | `tests/test_capture_lifetime.py` | R16 |
| **11.5** tracer tiers | ⬜ | `tests/test_tracer_tiers.py` | R17 |
| **11.6** multiple BPs | ⬜ | `tests/test_multiple_matching_breakpoints.py` | R20 |
| **11.7** queue overflow | ⬜ | tests | R23 |
| **11.8** file_line BP | ⬜ | `tests/test_file_line_bp.py` | R7, R22 |
| **12.1** COMPLIANCE_CHECKLIST | ⬜ | `COMPLIANCE_CHECKLIST.md` | R34 |
| _integration_ | ⬜ | `test_integration.py`, `test_concurrency.py` | R1, R13 |

---

## PR-13 — `chore/ci-hardening`

| Task | Status | Files | Req |
|------|--------|-------|-----|
| **12.2** purity script final | ⬜ | `scripts/check_target_purity.sh` | R3 |
| **12.3** docker CI job | ⬜ | `.github/workflows/ci.yml` | R32 |

---

## PR-14 — `docs/readme`

### Task 14.1 — README (manual)

| Field | Detail |
|-------|--------|
| **Status** | ⬜ todo |
| **Branch** | `docs/readme` |
| **Requirements** | R33 |
| **Files** | `README.md` |
| **Rule** | **Human-written** — not AI-generated |

**Placeholder commit:** `docs: add README (manual)`

**Actual commit hash:** · **Actual commit message:** · **Verification:** · **Notes:**

---

*Last updated: 2026-06-15 — task 1.1 complete*
