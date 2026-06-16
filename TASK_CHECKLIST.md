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
| PR-05 | `feat/agent-breakpoint-registry` | 5.1–5.5 | 5/5 | ✅ merged |
| PR-06 | `feat/agent-safe-serializer` | 7.1–7.2 | 2/2 | ✅ merged |
| PR-07 | `feat/agent-capture-worker` | 6.1–6.3 | 3/3 | ✅ merged |
| PR-08 | `feat/agent-tracer` | 8.1–8.6 | 6/6 | ✅ ready for PR |
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
| **Status** | ✅ done |
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
Pushed to origin/feat/agent-breakpoint-registry; CI green
```

**Placeholder commit:** `feat(agent): support multiple BPs per name/line`

**Actual commit hash:** `b7e13d8`

**Actual commit message:**

```text
feat(agent): support multiple BPs per name/line

- Add get_matching_breakpoint_ids for call and line events
- Return all bp ids sharing co_name, qualname, or file+line (no deduplication)
- Add registry tests for multiple BPs on same target (34 total pytest)
- Update TASK_CHECKLIST and CONTEXT: task 5.3 committed, 5.4 done
```

**Notes:**

---

### Task 5.5 — breakpoints.yaml seed loader

| Field | Detail |
|-------|--------|
| **Status** | ✅ done |
| **Branch** | `feat/agent-breakpoint-registry` |
| **Requirements** | R29 |
| **Files** | `breakpoints.yaml`, `agent/breakpoints.py`, `tests/test_breakpoints_yaml.py`, `requirements.txt` |
| **Done when** | Loader registers function, method, file_line examples |

**Delivered:**

- `breakpoints.yaml` — seed examples: function `compute`, method `AdditionEngine.add`, file_line `addition.py:5`
- `breakpoint_from_dict`, `load_breakpoints_yaml` — PyYAML loader into registry
- `requirements.txt` — `PyYAML>=6.0,<7`
- `tests/test_breakpoints_yaml.py` — 4 loader tests

**Verification:**

```text
pytest tests/test_breakpoints_yaml.py -q → 4 passed
pytest tests/ -q → 38 passed
Merged via PR #5 (merge 4046196); CI green
```

**Placeholder commit:** `feat(agent): load breakpoints.yaml seed config`

**Actual commit hash:** `20164ec`

**Actual commit message:**

```text
feat(agent): load breakpoints.yaml seed config

- Add breakpoints.yaml with function, method, and file_line seed examples
- Add breakpoint_from_dict and load_breakpoints_yaml to agent/breakpoints.py
- Add PyYAML to requirements.txt; add tests/test_breakpoints_yaml.py
- Update TASK_CHECKLIST and CONTEXT: PR-05 complete, PR draft ready
```

**Notes:**

---

**PR-05 merge checklist:**

- [x] All tasks 5.1–5.5 ✅
- [x] CI green on PR
- [x] PR merged to `main` (PR #5, merge `4046196`)

**Pull request draft** *(copy to GitHub after task 5.5 push):*

| Field | Value |
|-------|--------|
| **When** | Now — after task 5.5 commit + push |
| **Base ← Compare** | `main` ← `feat/agent-breakpoint-registry` |
| **Title** | `feat(agent): breakpoint registry (PR-05)` |

**Description** (paste into GitHub PR body):

```markdown
## Summary
Breakpoint matching, thread-safe registry with O(1) indexes, multi-BP support, and YAML seed config.

## Tasks included

### Task 5.1 — Path normalization
- **Files:** `agent/breakpoints.py`, `tests/test_breakpoints.py`
- **Behavior:** `normalize_path()` via `Path.resolve()`

### Task 5.2 — Matchers
- **Files:** `agent/breakpoints.py`
- **Behavior:** function/method/file_line matchers + dispatcher

### Task 5.3 — BreakpointRegistry
- **Files:** `agent/registry.py`, `tests/test_registry.py`
- **Behavior:** Thread-safe registry with O(1) indexes

### Task 5.4 — Multiple BPs per target
- **Files:** `agent/registry.py`
- **Behavior:** `get_matching_breakpoint_ids` — all ids, no deduplication

### Task 5.5 — YAML seed
- **Files:** `breakpoints.yaml`, loader in `agent/breakpoints.py`, `requirements.txt`
- **Behavior:** Load function, method, file_line seed breakpoints at startup

## Requirements touched
R5–R7 · R20–R22 · R29

## Test plan
- [ ] `ci` workflow green
- [ ] `pytest tests/ -q` — 38 passed

## Merge notes
Depends on PR-04. Enables PR-08 (tracer) and PR-09 (control API).
```

---

## PR-06 — `feat/agent-safe-serializer`

### Task 7.1 — SafeSerializer

| Field | Detail |
|-------|--------|
| **Status** | ✅ done (commit `3517cac`, CI green) |
| **Branch** | `feat/agent-safe-serializer` |
| **Requirements** | R30 |
| **Files** | `agent/serializer.py`, `tests/test_serializer.py` |
| **Done when** | Circular refs, callables, generators, bytes, depth limit; tests pass |

**Delivered:**

- `SafeSerializer` — `serialize()` + `serialize_locals()` with depth limit (default 5)
- Fallbacks: bytes, callables, generators, circular refs, nested dict/list/set
- Never raises on pathological inputs (BadRepr → safe fallback)

**Verification:**

```text
pytest tests/test_serializer.py -q → 7 passed
pytest tests/ -q → 45 passed
```

**Placeholder commit:** `feat(agent): add SafeSerializer with type fallbacks`

**Actual commit hash:** `3517cac`

**Actual commit message:**

```text
feat(agent): add SafeSerializer with type fallbacks
- Add SafeSerializer with depth limit, circular ref guard, type fallbacks
- Handle bytes, callables, generators; serialize_locals never raises
- Add tests/test_serializer.py with 7 cases (45 total pytest)
- Update TASK_CHECKLIST and CONTEXT: PR-05 merged, PR-06 task 7.1 done
```

**Notes:** Pushed; CI green on branch.

---

### Task 7.2 — Pathological serializer inputs

| Field | Detail |
|-------|--------|
| **Status** | ✅ done (commit `b0390a2`, CI green) |
| **Branch** | `feat/agent-safe-serializer` |
| **Requirements** | R31 |
| **Files** | `agent/serializer.py`, `tests/test_serializer.py` |
| **Done when** | Extra pathological cases; `serialize` / `serialize_locals` never raise |

**Delivered:**

- Per-item try/except in dict/list branches; bad dict keys → `<bad_key TypeName>`
- Tests: circular list, mutual dict cycle, infinite `__repr__`, bad keys, long bytes, bytearray, mixed basket, parametrized never-raises sweep

**Verification:**

```text
pytest tests/test_serializer.py -q → 15 passed
pytest tests/ -q → 53 passed
Merged via PR #6 (merge edfbce1); CI green
```

**Placeholder commit:** `test(agent): pathological SafeSerializer cases (R31)`

**Actual commit hash:** `b0390a2`

**Actual commit message:**

```text
test(agent): pathological SafeSerializer cases (R31)
- Harden dict/list serialization with per-item guards and bad-key fallback
- Add 8 pathological tests (circular list, mutual cycle, infinite repr, etc.)
- pytest 53 passed; update TASK_CHECKLIST and CONTEXT
```

**Notes:** Pushed; merged via PR #6.

---

| Task | Status | Files | Req |
|------|--------|-------|-----|
| **7.2** pathological inputs | ✅ | tests | R31 |

**PR-06 merge checklist:**

- [x] All tasks 7.1–7.2 ✅
- [x] CI green on PR
- [x] PR merged to `main` (PR #6, merge `edfbce1`)

**Pull request draft** *(copy to GitHub after task 7.2 push):*

| Field | Value |
|-------|--------|
| **When** | Merged — PR #6 (`edfbce1`) |
| **Base ← Compare** | `main` ← `feat/agent-safe-serializer` |
| **Title** | `feat(agent): safe serializer (PR-06)` |

**Description** (paste into GitHub PR body):

```markdown
## Summary
Defensive JSON-oriented serialization for captured locals — type fallbacks, depth limit, circular refs, and pathological-input hardening (R30, R31).

## Tasks included

### Task 7.1 — SafeSerializer
- **Files:** `agent/serializer.py`, `tests/test_serializer.py`
- **Behavior:** `serialize()` + `serialize_locals()`; bytes, callables, generators, circular refs, depth limit
- **Verification:** 7 tests; pytest 45 passed

### Task 7.2 — Pathological inputs
- **Files:** `agent/serializer.py`, `tests/test_serializer.py`
- **Behavior:** Per-item dict/list guards; bad keys; circular list/mutual dict; infinite repr; never-raises sweep
- **Verification:** 15 serializer tests; pytest 53 passed

## Test plan
- [x] `pytest tests/test_serializer.py -q` → 15 passed
- [x] `pytest tests/ -q` → 53 passed
- [x] CI green
```

---

## PR-07 — `feat/agent-capture-worker`

### Task 6.1 — Synchronous RawCapture from live frames

| Field | Detail |
|-------|--------|
| **Status** | ✅ done (commit `37e7b41`, CI green) |
| **Branch** | `feat/agent-capture-worker` |
| **Requirements** | R8, R9, R19 |
| **Files** | `agent/capture.py`, `tests/test_capture.py` |
| **Done when** | `f_back` walk, shallow `dict(f_locals)`, return value from arg; tests pass |

**Delivered:**

- `capture_stack_frames()` — walk `f_back` chain, innermost first; normalized paths via `normalize_path`
- `capture_raw()` — build immutable `RawCapture` with thread id, monotonic timestamp, optional return value on `'return'`
- No live `frame` references cross capture boundary (§5.5)

**Verification:**

```text
pytest tests/test_capture.py -q → 8 passed
pytest tests/ -q → 61 passed
```

**Placeholder commit:** `feat(agent): add synchronous RawCapture from live frames`

**Actual commit hash:** `37e7b41`

**Actual commit message:**

```text
feat(agent): add synchronous RawCapture from live frames
- Add capture_stack_frames and capture_raw in agent/capture.py
- Walk f_back chain with shallow dict(f_locals) and normalized paths
- Capture return_value on RETURN events; immutable RawCapture only (R8, R9, R19)
- Add tests/test_capture.py with 8 cases (61 total pytest)
- Update TASK_CHECKLIST, CONTEXT, DEMO_COMMANDS
```

**Notes:** Pushed; CI green.

---

### Task 6.2 — SnapshotWorker

| Field | Detail |
|-------|--------|
| **Status** | ✅ done (commit `7fb47c6`, CI green) |
| **Branch** | `feat/agent-capture-worker` |
| **Requirements** | R11, R12 |
| **Files** | `agent/worker.py`, `tests/test_worker.py` |
| **Done when** | Build Snapshot from RawCapture, serialize locals, write JSON; worker thread |

**Delivered:**

- `build_snapshot()` / `snapshot_to_dict()` — registry lookup, SafeSerializer on locals + return value
- `SnapshotWorker` — background thread, `sys.settrace(None)` + `threading.settrace(None)` on start
- Writes `snapshots/{snapshot_id}.json`; optional stdout via `EMIT_STDOUT` env

**Verification:**

```text
pytest tests/test_worker.py -q → 7 passed
pytest tests/ -q → 68 passed
```

**Placeholder commit:** `feat(agent): add SnapshotWorker background thread`

**Actual commit hash:** `7fb47c6`

**Actual commit message:**

```text
feat(agent): add SnapshotWorker background thread
- Add build_snapshot and snapshot_to_dict in agent/worker.py
- SnapshotWorker consumes queue, serializes locals, writes snapshots/*.json
- Disable tracing on worker thread; optional EMIT_STDOUT (R11, R12)
- Add tests/test_worker.py with 7 cases (68 total pytest)
- Update TASK_CHECKLIST, CONTEXT, DEMO_COMMANDS
```

**Notes:** Pushed; CI green.

---

### Task 6.3 — Bounded queue overflow policy

| Field | Detail |
|-------|--------|
| **Status** | ✅ done (commit `211c9a4`, CI green) |
| **Branch** | `feat/agent-capture-worker` |
| **Requirements** | R23 |
| **Files** | `agent/worker.py`, `tests/test_worker.py` |
| **Done when** | `Queue(maxsize=1000)`, `put_nowait`, drop silently, rate-limited stderr |

**Delivered:**

- `create_capture_queue()` — bounded queue (default maxsize 1000)
- `enqueue_capture()` — non-blocking `put_nowait`; never raises to caller
- `DropLogger` — rate-limited `snapshot dropped: queue full` on agent stderr

**Verification:**

```text
pytest tests/test_worker.py -q → 13 passed
pytest tests/ -q → 74 passed
```

**Placeholder commit:** `feat(agent): bounded capture queue with loss-tolerant overflow`

**Actual commit hash:** `211c9a4`

**Actual commit message:**

```text
feat(agent): bounded capture queue with loss-tolerant overflow
- Add create_capture_queue (maxsize=1000) and enqueue_capture via put_nowait
- DropLogger rate-limits snapshot dropped: queue full stderr warnings (R23)
- Extend tests/test_worker.py with 6 overflow cases (74 total pytest)
- Update TASK_CHECKLIST with PR-07 draft, CONTEXT, DEMO_COMMANDS
```

**Notes:** Pushed; merged via PR #7.

---

| Task | Status | Files | Req |
|------|--------|-------|-----|
| **6.1** sync RawCapture | ✅ | `agent/capture.py` | R8, R9, R19 |
| **6.2** SnapshotWorker | ✅ | `agent/worker.py` | R11, R12 |
| **6.3** queue overflow | ✅ | `agent/worker.py` | R23 |

**PR-07 merge checklist:**

- [x] All tasks 6.1–6.3 ✅
- [x] CI green on PR
- [x] PR merged to `main` (PR #7, merge `03279c0`)

**Pull request draft** *(merged — PR #7, `03279c0`):*

| Field | Value |
|-------|--------|
| **When** | Merged — PR #7 (`03279c0`) |
| **Base ← Compare** | `main` ← `feat/agent-capture-worker` |
| **Title** | `feat(agent): capture worker pipeline (PR-07)` |

**Description** (paste into GitHub PR body):

```markdown
## Summary
Sync capture from live frames + async snapshot pipeline — worker serializes copied data and writes JSON; bounded loss-tolerant queue (R8–R12, R19, R23).

## Tasks included

### Task 6.1 — Synchronous RawCapture
- **Files:** `agent/capture.py`, `tests/test_capture.py`
- **Behavior:** `f_back` walk, shallow `dict(f_locals)`, return value on RETURN
- **Verification:** 8 tests; pytest 61 passed (after 6.1)

### Task 6.2 — SnapshotWorker
- **Files:** `agent/worker.py`, `tests/test_worker.py`
- **Behavior:** Build Snapshot from RawCapture, SafeSerializer, JSON to `snapshots/`; worker thread disables tracing
- **Verification:** 7 worker tests; pytest 68 passed (after 6.2)

### Task 6.3 — Queue overflow policy
- **Files:** `agent/worker.py`, `tests/test_worker.py`
- **Behavior:** `Queue(maxsize=1000)`, `enqueue_capture` via `put_nowait`, rate-limited drop warnings (§5.8.1)
- **Verification:** 13 worker tests; pytest 74 passed

## Test plan
- [x] `pytest tests/test_capture.py tests/test_worker.py -q` → 21 passed
- [x] `pytest tests/ -q` → 74 passed
- [x] CI green
```

---

## PR-08 — `feat/agent-tracer` ⚠️ critical path

### Task 8.1 — Trace installer

| Field | Detail |
|-------|--------|
| **Status** | ✅ done (commit `2bea1ba`, CI green) |
| **Branch** | `feat/agent-tracer` |
| **Requirements** | R15 |
| **Files** | `agent/installer.py`, `tests/test_installer.py` |
| **Done when** | Install/remove `sys.settrace` + `threading.settrace`; tests pass |

**Delivered:**

- `TraceInstaller` — `install()` / `remove()` with thread-safe state
- `install_trace()` / `remove_trace()` — convenience helpers for bootstrap
- New threads inherit tracing via `threading.settrace`

**Verification:**

```text
pytest tests/test_installer.py -q → 6 passed
pytest tests/ -q → 80 passed
```

**Placeholder commit:** `feat(agent): add trace installer (sys + threading settrace)`

**Actual commit hash:** `2bea1ba`

**Actual commit message:**

```text
feat(agent): add trace installer (sys + threading settrace)
- Add TraceInstaller with install/remove for sys and threading hooks
- Add install_trace and remove_trace helpers for bootstrap (R15)
- Add tests/test_installer.py with 6 cases (80 total pytest)
- Update TASK_CHECKLIST (PR-07 merged), CONTEXT, DEMO_COMMANDS
```

**Notes:** Pushed; CI green.

---

### Task 8.2 — global_trace (ENTRY capture)

| Field | Detail |
|-------|--------|
| **Status** | ✅ done (commit `13439df`, CI green) |
| **Branch** | `feat/agent-tracer` |
| **Requirements** | R4, R8, R13 |
| **Files** | `agent/tracer.py`, `tests/test_tracer_global.py` |
| **Done when** | Fast reject, ENTRY/BOTH capture on `'call'`, enqueue RawCapture; hit → snapshot |

**Delivered:**

- `Tracer.global_trace` — non-`'call'` fast return; O(1) registry fast reject (§5.3)
- ENTRY/BOTH → sync `RawCapture` + `enqueue_capture`; RETURN/BOTH → install function local trace stub
- Error isolation — trace callback never crashes target
- End-to-end test: ENTRY hit → worker writes JSON snapshot

**Verification:**

```text
pytest tests/test_tracer_global.py -q → 8 passed
pytest tests/ -q → 88 passed
```

**Placeholder commit:** `feat(agent): add global_trace with fast reject and ENTRY capture`

**Actual commit hash:** `13439df`

**Actual commit message:**

```text
feat(agent): add global_trace with fast reject and ENTRY capture
- Add Tracer.global_trace with O(1) fast reject and ENTRY/BOTH capture (§5.3)
- Enqueue RawCapture via capture_raw + enqueue_capture; install local trace stub for RETURN/BOTH
- Add tests/test_tracer_global.py with 8 cases including snapshot E2E (88 total pytest)
- Update TASK_CHECKLIST, CONTEXT, DEMO_COMMANDS
```

**Notes:** Pushed; CI green.

---

### Task 8.3 — local_trace_for_function_breakpoint

| Field | Detail |
|-------|--------|
| **Status** | ✅ done (commit `0e05fc3`, CI green) |
| **Branch** | `feat/agent-tracer` |
| **Requirements** | R16, R19 |
| **Files** | `agent/tracer.py`, `tests/test_capture_lifetime.py`, `tests/test_tracer_global.py` |
| **Done when** | RETURN/BOTH capture on `'return'` with return_value + final locals |

**Delivered:**

- `local_trace_for_function_breakpoint` — per-bp RawCapture on `'return'` using trace `arg`
- Uses `_frame_return_bps` from call-time install; ignores `'line'` events
- `tests/test_capture_lifetime.py` — RETURN locals, BOTH call+return, multi-BP, no frame refs

**Verification:**

```text
pytest tests/test_capture_lifetime.py -q → 4 passed
pytest tests/test_tracer_global.py -q → 8 passed
pytest tests/ -q → 92 passed
```

**Placeholder commit:** `feat(agent): add local_trace_for_function_breakpoint RETURN capture`

**Actual commit hash:** `0e05fc3`

**Actual commit message:**

```text
feat(agent): add local_trace_for_function_breakpoint RETURN capture
- Capture RETURN/BOTH on return event with return_value and final locals
- One RawCapture per matching breakpoint_id (§5.3.1)
- Add tests/test_capture_lifetime.py; update test_tracer_global BOTH/RETURN cases
- pytest 92 passed; update TASK_CHECKLIST, CONTEXT, DEMO_COMMANDS
```

**Notes:** Pushed; CI green.

---

### Task 8.4 — local_trace_for_file_line_breakpoint

| Field | Detail |
|-------|--------|
| **Status** | ✅ done (commit `afeba41`, CI green) |
| **Branch** | `feat/agent-tracer` |
| **Requirements** | R7, R17, R22 |
| **Files** | `agent/tracer.py`, `tests/test_tracer_tiers.py` |
| **Done when** | Line events in watched files only; file_line ENTRY/RETURN capture |

**Delivered:**

- `local_trace_for_file_line_breakpoint` — installed on `'call'` into `watched_files`
- ENTRY/BOTH → capture on `'line'`; RETURN/BOTH → capture on `'return'` at matching line
- `_capture_file_line_hits` helper; global trace still ignores non-`'call'` events (R17)
- `tests/test_tracer_tiers.py` — tier isolation + `AdditionEngine.add` file_line hits

**Verification:**

```text
pytest tests/test_tracer_tiers.py -q → 5 passed
pytest tests/ -q → 97 passed
```

**Placeholder commit:** `feat(agent): add local_trace_for_file_line_breakpoint`

**Actual commit hash:** `afeba41`

**Actual commit message:**

```text
feat(agent): add local_trace_for_file_line_breakpoint
- Install file-line local trace on call into watched_files (§5.3)
- Capture ENTRY/BOTH on line; RETURN/BOTH on return at matching file+line
- Add tests/test_tracer_tiers.py with 5 tier isolation cases (97 total pytest)
- Update TASK_CHECKLIST, CONTEXT, DEMO_COMMANDS
```

**Notes:** Pushed; CI green.

---

### Task 8.5 — Combined local trace

| Field | Detail |
|-------|--------|
| **Status** | ✅ done (commit `00f8f73`, CI green) |
| **Branch** | `feat/agent-tracer` |
| **Requirements** | R18 |
| **Files** | `agent/tracer.py`, `tests/test_tracer_combined.py` |
| **Done when** | Single local trace dispatches function RETURN/BOTH + file_line on overlap |

**Delivered:**

- `local_trace_combined` — one callback when RETURN/BOTH method BP + watched file overlap (§5.3 step 5)
- Dispatches `'line'` → file_line; `'return'` → function + file_line captures
- `tests/test_tracer_combined.py` — BOTH+ENTRY, RETURN+RETURN, RETURN+ENTRY on `AdditionEngine.add`

**Verification:**

```text
pytest tests/test_tracer_combined.py -q → 3 passed
pytest tests/ -q → 100 passed
```

**Placeholder commit:** `feat(agent): add combined local trace dispatcher`

**Actual commit hash:** `00f8f73`

**Actual commit message:**

```text
feat(agent): add combined local trace dispatcher
- Add local_trace_combined when RETURN/BOTH and file_line overlap (§5.3 step 5, R18)
- Dispatch line hits and dual return captures from one local trace callback
- Add tests/test_tracer_combined.py with 3 AdditionEngine.add overlap cases
- pytest 100 passed; update TASK_CHECKLIST, CONTEXT, DEMO_COMMANDS
```

**Notes:** Pushed; CI green.

---

### Task 8.6 — Agent thread isolation

| Field | Detail |
|-------|--------|
| **Status** | ✅ done (commit pending) |
| **Branch** | `feat/agent-tracer` |
| **Requirements** | R24 |
| **Files** | `agent/installer.py`, `agent/worker.py`, `agent/control_server.py`, `tests/test_agent_thread_isolation.py` |
| **Done when** | Agent threads disable tracing; no self-snapshots |

**Delivered:**

- `disable_tracing_on_current_thread()` in `agent/installer.py` (§5.11)
- `SnapshotWorker` + `AgentControlServer` call it on thread start
- Minimal control server stub (`501` on GET) — full API in PR-09
- `tests/test_agent_thread_isolation.py` — worker + control server isolation

**Verification:**

```text
pytest tests/test_agent_thread_isolation.py -q → 4 passed
pytest tests/ -q → 104 passed
```

**Placeholder commit:** `feat(agent): disable tracing on agent-owned threads`

**Actual commit hash:**

**Actual commit message:**

**Notes:**

---

| Task | Status | Files | Req |
|------|--------|-------|-----|
| **8.1** installer | ✅ | `agent/installer.py` | R15 |
| **8.2** global_trace | ✅ | `agent/tracer.py` | R4, R8, R13 |
| **8.3** local_trace function | ✅ | `agent/tracer.py` | R16, R19 |
| **8.4** local_trace file_line | ✅ | `agent/tracer.py` | R7, R17 |
| **8.5** combined local trace | ✅ | `agent/tracer.py` | R18 |
| **8.6** agent thread isolation | ✅ | `agent/installer.py`, `worker`, `control_server` | R24 |

**PR-08 merge checklist:**

- [x] All tasks 8.1–8.6 ✅
- [ ] CI green on PR
- [ ] PR merged to `main`

**Pull request draft** *(copy to GitHub after task 8.6 push):*

| Field | Value |
|-------|--------|
| **When** | Now — after task 8.6 commit + push |
| **Base ← Compare** | `main` ← `feat/agent-tracer` |
| **Title** | `feat(agent): two-tier tracer (PR-08)` |

**Description** (paste into GitHub PR body):

```markdown
## Summary
Core sys.settrace instrumentation — two-tier global/local trace, capture pipeline integration, agent thread isolation (R4, R8, R13–R19, R24).

## Tasks included

### Task 8.1 — Trace installer
- **Files:** `agent/installer.py`, `tests/test_installer.py`
- **Behavior:** `sys.settrace` + `threading.settrace` install/remove

### Task 8.2 — global_trace
- **Files:** `agent/tracer.py`, `tests/test_tracer_global.py`
- **Behavior:** Fast reject, ENTRY/BOTH capture on call

### Task 8.3 — local_trace function
- **Files:** `agent/tracer.py`, `tests/test_capture_lifetime.py`
- **Behavior:** RETURN/BOTH capture on return

### Task 8.4 — local_trace file_line
- **Files:** `agent/tracer.py`, `tests/test_tracer_tiers.py`
- **Behavior:** Line events in watched files only

### Task 8.5 — Combined local trace
- **Files:** `agent/tracer.py`, `tests/test_tracer_combined.py`
- **Behavior:** Single dispatcher when function + file_line overlap

### Task 8.6 — Agent thread isolation
- **Files:** `agent/installer.py`, `agent/worker.py`, `agent/control_server.py`, `tests/test_agent_thread_isolation.py`
- **Behavior:** `disable_tracing_on_current_thread()` on agent threads

## Test plan
- [ ] `pytest tests/test_installer.py tests/test_tracer_global.py tests/test_capture_lifetime.py tests/test_tracer_tiers.py tests/test_tracer_combined.py tests/test_agent_thread_isolation.py -q` → 30 passed
- [ ] `pytest tests/ -q` → 104 passed
- [ ] CI green
```

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
