# Compliance Checklist — HyperProbe PoC

Maps assignment requirements **R1–R34** to automated tests, CI jobs, or manual verification steps.  
Design reference: `notes/ARCHITECTURE_V2.md` · Implementation: `notes/IMPLEMENTATION_PLAN.md`

**Last verified:** 2026-06-16 · **pytest:** 159 passed · **Branch:** `chore/ci-hardening` (PR-13)

---

## Quick verification

```powershell
# Full automated suite + target purity (matches CI)
pytest tests/ -q
bash scripts/check_target_purity.sh

# PR-12 compliance test files
pytest tests/test_capture_lifetime.py tests/test_tracer_tiers.py `
  tests/test_multiple_matching_breakpoints.py tests/test_queue_overflow.py `
  tests/test_file_line_bp.py -q
```

**Manual demos** (see `notes/DEMO_COMMANDS.md`):

- Docker one-command startup (R32): `docker compose up --build`
- Calculator HTTP (R1): `curl http://localhost:8080/calculate?op=add&a=10&b=20`
- Runtime breakpoint (R25): `curl -X POST http://localhost:9090/breakpoints ...`

---

## Requirement matrix

| ID | Requirement | Evidence | Status |
|----|-------------|----------|--------|
| **R1** | HTTP `GET /calculate?op=add&a=10&b=20` returns JSON result | `tests/test_target_http.py::test_calculate_add_returns_json`; `tests/test_bootstrap.py::test_bootstrap_calculate_produces_snapshot_with_stack_frames` | ✅ |
| **R2** | ≥3 nested layers (handler → service → engine) visible in stack | `tests/test_bootstrap.py` — snapshot `stack_frames` includes `AdditionEngine.add`; `tests/test_capture.py::test_capture_includes_caller_locals` | ✅ |
| **R3** | Target code: zero logging/tracing/agent imports | CI: `scripts/check_target_purity.sh` → `target_purity_check.py`; `tests/test_target_purity_script.py`; `tests/test_target_http.py::test_target_tree_has_no_agent_imports` | ✅ |
| **R4** | Agent attaches externally (bootstrap + settrace, no target edits) | `agent/bootstrap.py`; `tests/test_bootstrap.py` | ✅ |
| **R5** | Dynamic breakpoint: function name (`co_name`) | `tests/test_tracer_global.py`; `tests/test_control_api.py`; `tests/test_control_server.py::test_post_function_breakpoint_returns_201` | ✅ |
| **R6** | Dynamic breakpoint: method (`co_qualname` exact) | `tests/test_tracer_global.py::test_global_trace_method_breakpoint_matches_qualname`; `tests/test_control_server.py::test_post_method_and_file_line_breakpoints` | ✅ |
| **R7** | Dynamic breakpoint: file + line | `tests/test_file_line_bp.py` | ✅ |
| **R8** | Capture current frame locals at hit time | `tests/test_capture.py`; `tests/test_tracer_global.py::test_global_trace_entry_enqueues_raw_capture` | ✅ |
| **R9** | Capture caller locals + full stack walk | `tests/test_capture.py::test_capture_includes_caller_locals`; `tests/test_capture.py::test_capture_stack_innermost_first` | ✅ |
| **R10** | Frame metadata (function, file, line, qualname) | `tests/test_worker.py::test_build_snapshot_includes_breakpoint_and_stack`; snapshot JSON schema in worker tests | ✅ |
| **R11** | Structured JSON snapshot files | `tests/test_worker.py::test_worker_writes_json_file`; `tests/test_bootstrap.py` | ✅ |
| **R12** | Optional stdout via `EMIT_STDOUT` | `tests/test_worker.py::test_worker_emit_stdout`; Docker compose sets `EMIT_STDOUT=1` | ✅ |
| **R13** | Non-halting instrumentation (no debugger pause) | Tracer returns immediately (`agent/tracer.py`); bootstrap HTTP completes under trace. **Gap:** dedicated concurrent load test not yet shipped (`test_concurrency.py` optional) | ⚠️ partial |
| **R14** | No modification of target source for observability | `target/` has no agent imports; purity script; agent wired only via bootstrap | ✅ |
| **R15** | Runtime API: `sys.settrace` + `threading.settrace` | `agent/installer.py`; `tests/test_installer.py` | ✅ |
| **R16** | Capture modes: ENTRY / RETURN / BOTH | `tests/test_capture_lifetime.py` | ✅ |
| **R17** | Two-tier trace (no global `'line'`/`'return'` events) | `tests/test_tracer_tiers.py` | ✅ |
| **R18** | Combined local trace (function RETURN/BOTH + file_line overlap) | `tests/test_tracer_combined.py` | ✅ |
| **R19** | RawCapture sync copy — never queue live frames | `tests/test_capture_lifetime.py::test_queued_raw_capture_has_no_frame_references`; `tests/test_capture.py::test_raw_capture_contains_only_copied_data` | ✅ |
| **R20** | Multiple BPs on same target → distinct snapshots | `tests/test_multiple_matching_breakpoints.py` | ✅ |
| **R21** | O(1) registry indexes (function/method/file_line) | `tests/test_registry.py` | ✅ |
| **R22** | Path normalization for file_line matching | `tests/test_breakpoints.py`; `tests/test_file_line_bp.py` | ✅ |
| **R23** | Bounded queue, non-blocking enqueue, drop on full | `tests/test_worker.py` (unit); `tests/test_queue_overflow.py` (target safety) | ✅ |
| **R24** | Agent threads disable tracing (`sys.settrace(None)`) | `tests/test_agent_thread_isolation.py`; `tests/test_worker.py::test_worker_disables_tracing_in_worker_thread` | ✅ |
| **R25** | Runtime `POST /breakpoints` without restart | `tests/test_control_api.py::test_dynamic_registration_via_control_api_produces_snapshot` | ✅ |
| **R26** | Runtime `GET /breakpoints` | `tests/test_control_server.py::test_get_breakpoints_lists_registered_items`; `tests/test_bootstrap.py::test_bootstrap_control_api_lists_seed_breakpoints` | ✅ |
| **R27** | POST validation (400 on bad payload) | `tests/test_control_server.py::test_post_missing_required_fields_returns_400`; `test_post_invalid_type_or_capture_mode_returns_400`; `test_post_malformed_json_returns_400` | ✅ |
| **R28** | Optional `id` in POST → server assigns uuid4 | `tests/test_breakpoints_yaml.py::test_breakpoint_from_dict_assigns_uuid_when_id_missing` (same `breakpoint_from_dict` as control API) | ✅ |
| **R29** | YAML seed loads function, method, file_line | `breakpoints.yaml`; `tests/test_breakpoints_yaml.py::test_load_repo_breakpoints_yaml_registers_all_seed_types` | ✅ |
| **R30** | Safe serialization (depth, cycles, callables) | `tests/test_serializer.py` | ✅ |
| **R31** | Error isolation in trace callback and worker | `agent/tracer.py` (BaseException handlers); `tests/test_worker.py::test_worker_continues_after_processing_error` | ✅ |
| **R32** | Docker one-command startup | `Dockerfile`, `docker-compose.yml`; CI: `.github/workflows/ci.yml` `docker` job (`docker compose build`); manual demo: `notes/DEMO_COMMANDS.md` | ✅ |
| **R33** | Human-written README | `README.md` — PR-14 task 14.1 (candidate-authored) | ⬜ pending |
| **R34** | This compliance checklist in repo | `COMPLIANCE_CHECKLIST.md` (this file) | ✅ |

**Legend:** ✅ automated or CI · ⚠️ partial / manual demo required · ⬜ not yet delivered

---

## PR-12 compliance test index

| File | Requirements |
|------|----------------|
| `tests/test_capture_lifetime.py` | R16, R19 |
| `tests/test_tracer_tiers.py` | R17 |
| `tests/test_multiple_matching_breakpoints.py` | R20 |
| `tests/test_queue_overflow.py` | R23 |
| `tests/test_file_line_bp.py` | R7, R22 |

---

## Known gaps (follow-up)

| Item | Requirement | Planned |
|------|-------------|---------|
| Concurrent HTTP load under trace | R13 | Optional `tests/test_concurrency.py` |
| Docker build in CI on every merge | R32 | `.github/workflows/ci.yml` docker job (task 12.3) |
| Candidate README | R33 | PR-14 task 14.1 |

---

## CI alignment

GitHub Actions workflow `.github/workflows/ci.yml` on every PR/push:

1. `pytest tests/ -q`
2. `bash scripts/check_target_purity.sh`

Covers automated evidence for R1–R31 and R32 docker build (except R13 concurrent load).
