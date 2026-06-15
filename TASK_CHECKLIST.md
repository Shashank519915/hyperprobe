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
| PR-03 | `feat/target-http-server` | 2.4–2.6 | 2/3 | 🔄 in progress |
| PR-04 | `feat/agent-data-models` | 4.1–4.2 | 0/2 | ⬜ todo |
| PR-05 | `feat/agent-breakpoint-registry` | 5.1–5.5 | 0/5 | ⬜ todo |
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
| **Status** | ✅ done (commit pending) |
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
HTTP smoke test on 127.0.0.1:18080 — add → 200/30.0, div/0 → 400, /unknown → 404
pytest tests/ -q → 11 passed
Dev: python -m target.server then curl localhost:8080/calculate?op=add&a=10&b=20
```

**Placeholder commit:** `feat(target): add ThreadingHTTPServer on :8080`

**Actual commit hash:**

**Actual commit message:**

**Notes:**

---

### Task 2.6 — HTTP tests + purity script update

| Status | ⬜ todo | **Files** | tests, `scripts/check_target_purity.sh` | **Req** | R3 |

**Placeholder commit:** `test(target): HTTP integration test without agent`

**Actual commit hash:** · **Actual commit message:** · **Verification:** · **Notes:**

---

**PR-03 merge checklist:**

- [ ] All tasks 2.4–2.6 ✅
- [ ] CI green on PR
- [ ] PR merged to `main`

**Pull request draft** *(fill after task 2.6 — then open PR on GitHub):*

| Field | Value |
|-------|--------|
| **When** | After task **2.6** is committed and pushed |
| **Base ← Compare** | `main` ← `feat/target-http-server` |
| **Title** | `feat(target): HTTP calculator server (PR-03)` |

---

## PR-04 — `feat/agent-data-models`

### Task 4.1 — Breakpoint models

| Status | ⬜ todo | **Files** | `agent/models.py` (Breakpoint, CaptureMode) | **Req** | R10, R16 |

**Placeholder commit:** `feat(agent): add Breakpoint and CaptureMode models`

**Actual commit hash:** · **Actual commit message:** · **Verification:** · **Notes:**

---

### Task 4.2 — RawCapture and Snapshot models

| Status | ⬜ todo | **Files** | `agent/models.py` | **Req** | R10, R20 |

**Placeholder commit:** `feat(agent): add RawCapture, Snapshot, StackFrame models`

**Actual commit hash:** · **Actual commit message:** · **Verification:** · **Notes:**

---

## PR-05 — `feat/agent-breakpoint-registry`

| Task | Status | Files | Req |
|------|--------|-------|-----|
| **5.1** path normalization | ⬜ | `agent/breakpoints.py` | R22 |
| **5.2** matchers | ⬜ | `agent/breakpoints.py`, `tests/test_breakpoints.py` | R5–R7 |
| **5.3** registry indexes | ⬜ | `agent/registry.py`, `tests/test_registry.py` | R21 |
| **5.4** multiple BPs | ⬜ | `agent/registry.py` | R20 |
| **5.5** breakpoints.yaml | ⬜ | `breakpoints.yaml` | R29 |

_Record commit hash / message / verification per task when done._

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
