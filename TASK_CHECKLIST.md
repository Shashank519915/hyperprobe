# Task Checklist — HyperProbe PoC

Track every implementation task. Update **Status**, **Actual commit**, and **Verification** as you go.  
Plan reference: `notes/IMPLEMENTATION_PLAN.md` · Design: `notes/ARCHITECTURE_V2.md`

**Status values:** `⬜ todo` · `🔄 in progress` · `✅ done` · `⛔ blocked`

**Commit rule:** Placeholder subjects live in the plan; after each task, write a **detailed** commit message (see `CODE_STYLE.md` §7) and record it here.

---

## Summary

| PR | Branch | Tasks | Done | Status |
|----|--------|-------|------|--------|
| PR-01 | `chore/repo-scaffold` | 1.1–1.4 | 3/4 | 🔄 in progress |
| PR-02 | `feat/target-core-layers` | 2.1–2.3 | 0/3 | ⬜ todo |
| PR-03 | `feat/target-http-server` | 2.4–2.6 | 0/3 | ⬜ todo |
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
| **Status** | ✅ done (commit pending) |
| **Branch** | `chore/repo-scaffold` |
| **Requirements** | R11 prep |
| **Files** | `snapshots/.gitkeep`, `TASK_CHECKLIST.md`, `CODE_STYLE.md`, `CONTEXT.md` |
| **Done when** | Tracking docs in repo root; design docs remain in gitignored `notes/` |

**Delivered:**

- `snapshots/.gitkeep` — keeps output dir in repo; `snapshots/*.json` gitignored
- `TASK_CHECKLIST.md`, `CODE_STYLE.md`, `CONTEXT.md` — committed tracking docs (this update)
- `CODE_STYLE.md` §7 — PR title/description rule (draft after last task in each PR)
- `notes/IMPLEMENTATION_PLAN.md` §9 — PR-01 draft template (local, gitignored)

**Note:** `ARCHITECTURE_V2.md` / `IMPLEMENTATION_PLAN.md` live in `notes/` (local only). Submission uses human-written `README.md` for architecture summary.

**Placeholder commit:** `chore: add snapshots dir and project tracking docs`

**Actual commit hash:**

**Actual commit message:**

**Verification:**

```text
snapshots/.gitkeep exists
.gitignore allows !snapshots/.gitkeep while ignoring snapshots/*.json
CODE_STYLE.md documents PR draft workflow (§7)
```

**Notes:**

---

### Task 1.4 — Package init files

| Field | Detail |
|-------|--------|
| **Status** | ⬜ todo |
| **Branch** | `chore/repo-scaffold` |
| **Requirements** | — |
| **Files** | `agent/__init__.py`, `target/__init__.py`, `tests/conftest.py` |
| **Done when** | `pytest` collects 0 tests, exit 0 |

**Placeholder commit:** `chore: add empty package init files`

**Actual commit hash:**

**Actual commit message:**

**Verification:**

**Notes:**

---

**PR-01 merge checklist:**

- [ ] All tasks 1.1–1.4 ✅
- [ ] CI green on PR
- [ ] PR merged to `main`

**Pull request draft** *(fill after task 1.4 — then open PR on GitHub):*

| Field | Value |
|-------|--------|
| **When** | After task **1.4** is committed and pushed |
| **Base ← Compare** | `main` ← `chore/repo-scaffold` |
| **Title** | `chore: repo scaffold (PR-01)` |
| **Description** | Full template in `notes/IMPLEMENTATION_PLAN.md` §9 (PR-01). Copy tasks 1.1–1.4 sections into GitHub PR body. |

---

## PR-02 — `feat/target-core-layers`

### Task 2.1 — Operation engines

| Field | Detail |
|-------|--------|
| **Status** | ⬜ todo |
| **Branch** | `feat/target-core-layers` |
| **Requirements** | R2, R3, R14 |
| **Files** | `target/engines/addition.py`, `subtraction.py`, `multiplication.py`, `division.py` |
| **Done when** | Pure engine logic; no I/O; no agent imports |

**Placeholder commit:** `feat(target): add operation engines (add/sub/mul/div)`

**Actual commit hash:** · **Actual commit message:** · **Verification:** · **Notes:**

---

### Task 2.2 — MathService

| Field | Detail |
|-------|--------|
| **Status** | ⬜ todo |
| **Branch** | `feat/target-core-layers` |
| **Requirements** | R2 |
| **Files** | `target/services/math_service.py` |
| **Done when** | `MathService.compute(op, a, b)` routes to engines |

**Placeholder commit:** `feat(target): add MathService routing to engines`

**Actual commit hash:** · **Actual commit message:** · **Verification:** · **Notes:**

---

### Task 2.3 — Unit tests (math layers)

| Field | Detail |
|-------|--------|
| **Status** | ⬜ todo |
| **Branch** | `feat/target-core-layers` |
| **Requirements** | R2 |
| **Files** | `tests/test_target_math.py` |
| **Done when** | pytest passes |

**Placeholder commit:** `test(target): unit test MathService and engines`

**Actual commit hash:** · **Actual commit message:** · **Verification:** · **Notes:**

---

## PR-03 — `feat/target-http-server`

### Task 2.4 — RouteHandler

| Status | ⬜ todo | **Files** | `target/handlers.py` | **Req** | R1, R2 |

**Placeholder commit:** `feat(target): add RouteHandler for /calculate`

**Actual commit hash:** · **Actual commit message:** · **Verification:** · **Notes:**

---

### Task 2.5 — ThreadingHTTPServer

| Status | ⬜ todo | **Files** | `target/server.py` | **Req** | R1 |

**Placeholder commit:** `feat(target): add ThreadingHTTPServer on :8080`

**Done when:** `curl localhost:8080/calculate?op=add&a=10&b=20` → JSON result

**Actual commit hash:** · **Actual commit message:** · **Verification:** · **Notes:**

---

### Task 2.6 — HTTP tests + purity script update

| Status | ⬜ todo | **Files** | tests, `scripts/check_target_purity.sh` | **Req** | R3 |

**Placeholder commit:** `test(target): HTTP integration test without agent`

**Actual commit hash:** · **Actual commit message:** · **Verification:** · **Notes:**

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
