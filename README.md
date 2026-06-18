# HyperProbe PoC

A runtime instrumentation proof-of-concept. The **target** (`target/`) is a plain HTTP calculator - handler, service, and engine layers, no observability code. The **agent** (`agent/`) attaches from outside at process start, registers breakpoints, and writes JSON snapshots when those breakpoints fire.


Python 3.12 · calculator on `:8080` · agent control API on `:9090`

---

## Quick start

You only need Docker. No local Python install required. Install Docker Desktop Signin/Signup. Keep the Docker Engine running in Docker Desktop.

```bash
git clone https://github.com/Shashank519915/hyperprobe.git
cd hyperprobe
docker compose up --build
```

In a second terminal:

```bash
curl "http://localhost:8080/calculate?op=add&a=10&b=20"
```

On Windows PowerShell use `curl.exe` instead of `curl`.

That's it. The seed breakpoints in `breakpoints.yaml` fire immediately on that request. Snapshot JSON files land in `./snapshots/` on your host (bind-mounted from the container), and each snapshot also prints as a JSON line in the compose logs because `EMIT_STDOUT=1` is set, which can be seen in Docker Deskto app and on terminal 1 to wehere we ran `docker compose up --build`.

To stop testing/running: `Ctrl+C` in the first terminal, then `docker compose down`.

---

## What the calculator does

`GET /calculate?op=<op>&a=<a>&b=<b>` supports `add`, `sub`, `mul`, and `div`.

```bash
curl "http://localhost:8080/calculate?op=add&a=10&b=20"
# response: {"op": "add", "a": 10.0, "b": 20.0, "result": 30.0}

curl "http://localhost:8080/calculate?op=div&a=10&b=0"
# response: 400 - division by zero

curl "http://localhost:8080/calculate?op=pow&a=2&b=3"
#response: 400 - unsupported operation
```

Every request goes through 3 application layers:

do_GET (target/server.py) → handle_calculate (target/handlers.py) → MathService.compute (target/services/math_service.py) → engine e.g. AdditionEngine.add (target/engines/addition.py)
An `add` request hits all three seed breakpoints. div,mul,sub / unsupported ops only hit the function breakpoint on compute as set in the breakpoint.yaml essentially.

---

## Viewing snapshots

After a calculate request, simply open the `/snapshots` folder and view teh JSON Snapshots easily.

or check `./snapshots/` on your host:

```bash
ls ./snapshots/
cat ./snapshots/<uuid>.json
```

Or watch compose logs in the first terminal and Docker Desktop logs.

**One `add` curl often produces three files** - one per seed breakpoint in `breakpoints.yaml` (`seed-function-compute`, `seed-method-add`, `seed-line-addition-return`). Other operations (e.g. `div`) usually produce one file (function `compute` only).

### Real Example - method breakpoint (ENTRY)

From `curl "http://localhost:8080/calculate?op=add&a=10&b=20"`, file `seed-method-add` 
(stack trimmed; full files also include stdlib HTTP/thread frames):

```json
{
  "snapshot_id": "0dda58d2-8b3c-446d-938a-d5926bc26bc9",
  "timestamp": "2026-06-17T07:38:10.134155+00:00",
  "breakpoint_id": "seed-method-add",
  "breakpoint": {
    "type": "method",
    "value": "AdditionEngine.add"
  },
  "capture_mode": "ENTRY",
  "event": "call",
  "thread_id": 129653133207232,
  "return_value": null,
  "stack_frames": [
    {
      "index": 0,
      "function": "add",
      "qualname": "AdditionEngine.add",
      "file": "/app/target/engines/addition.py",
      "line": 4,
      "locals": { "a": 10.0, "b": 20.0 }
    },
    {
      "index": 1,
      "function": "compute",
      "qualname": "MathService.compute",
      "file": "/app/target/services/math_service.py",
      "line": 19,
      "locals": { "op": "add", "a": 10.0, "b": 20.0 }
    },
    {
      "index": 2,
      "function": "handle_calculate",
      "qualname": "RouteHandler.handle_calculate",
      "file": "/app/target/handlers.py",
      "line": 14,
      "locals": {
        "query_string": "op=add&a=10&b=20",
        "op": "add",
        "a": 10.0,
        "b": 20.0
      }
    },
    {
      "index": 3,
      "function": "do_GET",
      "qualname": "_CalculatorHTTPRequestHandler.do_GET",
      "file": "/app/target/server.py",
      "line": 30,
      "locals": { "parsed": ["", "", "/calculate", "", "op=add&a=10&b=20", ""] }
    }
  ]
}
```

Index 0 is the innermost frame (where the breakpoint hits). Indices 0–2 are the three calculator layers; index 3 is the HTTP handler in `server.py`. We can clearly see the local variables and lnes of code of execution count captures.

### Example - file+line breakpoint (RETURN)

Same request, third snapshot - RETURN capture on `addition.py` line 5 with the computed result:

```json
{
  "snapshot_id": "aeebf59f-d811-4d45-b7e3-a6a142134116",
  "breakpoint_id": "seed-line-addition-return",
  "capture_mode": "RETURN",
  "event": "return",
  "return_value": 30.0,
  "stack_frames": [
    {
      "index": 0,
      "function": "add",
      "qualname": "AdditionEngine.add",
      "file": "/app/target/engines/addition.py",
      "line": 5,
      "locals": { "a": 10.0, "b": 20.0 }
    }
  ]
}
```

(`stack_frames` truncated here; the on-disk file includes the full caller chain like the ENTRY example above.)

---

## Runtime breakpoint demo

Seed breakpoints from `breakpoints.yaml` load at startup. You can register new ones without restarting:

```bash
# see what's already registered
curl http://localhost:9090/breakpoints

# register a new one
curl -X POST http://localhost:9090/breakpoints \
  -H "Content-Type: application/json" \
  -d '{"type":"method","value":"AdditionEngine.add","capture_mode":"ENTRY"}'

# trigger it
curl "http://localhost:8080/calculate?op=add&a=5&b=7"
```

A new snapshot file appears immediately. No restart. The tracer picks it up on the next matching call.

Three breakpoint types are supported:
`function` matches on -> any function named `value` -> like `"value": "compute"`
`method`matches on -> exact class.method qualname -> like `"value": "AdditionEngine.add"` 
`file_line` matches on -> specific file + line number -> like `"file": "target/engines/addition.py", "line": 5` 

Capture modes: `ENTRY` (on call), `RETURN` (on return, includes return value), `BOTH`.

The POST returns 201 with an assigned ID. 400 on bad input or input whihc returns bad output.

---

## How the instrumentation works

The calculator never imports the agent. There is no logging or tracing code in `target/`(the http calculator). Snapshots happen because we launch through the agent and Python gives us a hook into execution and we use quque workers to patch snapshots in json formats and save in files and return to logs.

The container entrypoint is `python -m agent.bootstrap`, not `python -m target.server`. 
Bootstrap starts everything in order: 
1) It loads `breakpoints.yaml` into an in-memory registry(BreakpointRegistery)
2) Starts a background worker thread (basically a bounded thread + bounded queue waiting to work) 
3) Installs `sys.settrace` on the main thread and `threading.settrace` so that calculator's HTTP request threads inherit tracing.
4) Then starts the agent control server on port 9090. 
5) Only after all of that does it import and start the calculator server (`create_server().serve_forever()`) on port 8080. 
The target never imports the agent, the bootstrap is the only place both sides are wired together.

When the calculator handles a request, the interpreter fires trace events on every function call. 
Inside Global Trace:
The global trace callback checks the function name and qualname against the BreakpointrRegistry in O(1) using indexed sets. If there's no match of breakpoint ids, it returns None immediately, costing almost nothing. On a match it copies the frame's locals with `dict(f_locals)` and walks the `f_back` chain to capture every caller's locals too - all of this happens synchronously inside the callback, before the callback returns, because frame objects are only valid during the trace event. That copied data goes into a `RawCapture` dataclass and is put onto a bounded queue with `put_nowait`. A separate SnapshotWorker thread picks it up, runs it through a JSON serializer (handles cycles, deep nesting, callables), and writes the file in `/snapshots`. The request thread never touches I/O.

For RETURN and file+line breakpoints, a scoped local trace function is installed on the matched frame at call time. The global trace only handles `'call'` events - it never processes `'line'` or `'return'` globally, which is the main thing that keeps overhead reasonable.

---

## Architecture decisions

1) The assignment says instrumentation must happen via runtime or native tooling APIs without modifying target source. Launching the target under an external entrypoint is the same pattern as `python -m pdb -m myapp`. The target modules are never edited; `target/` can be run standalone with `python -m target.server` and works fine.

2) if you enable `'line'` events globally, every single line in every traced thread fires a callback. That's roughly a 50–70% throughput hit. The fix is to only install line-level tracing on frames in files that have active file+line breakpoints. The global callback stays cheap; line overhead is proportional to code in watched files only.

3) Sync capture, async write - locals must be copied inside the trace callback. basically copy in callback; serialize/write in worker.

4) the queue has a hard cap of 1000 items. Under sustained load, snapshots are dropped silently (with a rate-limited warning to agent stderr). The calculator always keeps serving.

---

## Limitations

`sys.settrace` fires a callback on every function call in traced threads. For this PoC that's acceptable. The two-tier design limits line-event overhead, and the async worker keeps serialization off the request path. But for a high-traffic production servicewe'd want to move to `sys.monitoring` (PEP 669, Python 3.12+), which lets you subscribe to specific event sets and activate monitoring per code object rather than process-wide. That would be the first production upgrade, whihc i also did on the: (https://github.com/Shashank519915/hyperprobe-v2) 

The control API on port 9090 has no authentication. Fine for localhost PoC currently; would need TLS and auth for prod.

---

## Running without Docker

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

pytest tests/ -q                  # 163 tests
python scripts/target_purity_check.py

python -m agent.bootstrap         # settrace backend (default)
```

---

## Repository layout

```
agent/             tracer, capture, worker, control API, bootstrap
target/            pristine calculator - handler, service, engines
tests/             163 pytest cases
Dockerfile         python:3.12-slim, ENTRYPOINT agent.bootstrap
docker-compose.yml ports 8080 + 9090, snapshot volume, EMIT_STDOUT
breakpoints.yaml   seed breakpoints (function, method, file+line)
COMPLIANCE_CHECKLIST.md   requirement-to-test mapping (R1–R34)
scripts/           target purity check
```

CI runs pytest, target purity scan, and `docker compose build` on every PR.