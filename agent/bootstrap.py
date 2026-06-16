"""Wire agent instrumentation + target server — process entrypoint (§5.1, R4)."""

from __future__ import annotations

import os
import queue
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from agent.breakpoints import load_breakpoints_yaml
from agent.control_server import (
    DEFAULT_CONTROL_HOST,
    DEFAULT_CONTROL_PORT,
    AgentControlServer,
)
from agent.installer import TraceInstaller, install_trace, remove_trace
from agent.registry import BreakpointRegistry
from agent.tracer import Tracer
from agent.worker import SnapshotWorker, create_capture_queue

if TYPE_CHECKING:
    from target.server import _CalculatorHTTPServer

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BREAKPOINTS_PATH = REPO_ROOT / "breakpoints.yaml"
DEFAULT_SNAPSHOTS_DIR = REPO_ROOT / "snapshots"


@dataclass
class AgentRuntime:
    """Wired agent components — worker, control API, and trace hooks."""

    registry: BreakpointRegistry
    capture_queue: queue.Queue
    worker: SnapshotWorker
    tracer: Tracer
    control_server: AgentControlServer
    installer: TraceInstaller

    def shutdown(self) -> None:
        self.control_server.stop()
        self.worker.stop()
        remove_trace(self.installer)


def start_agent(
    *,
    breakpoints_path: Path | str = DEFAULT_BREAKPOINTS_PATH,
    snapshots_dir: Path | str = DEFAULT_SNAPSHOTS_DIR,
    control_host: str = DEFAULT_CONTROL_HOST,
    control_port: int = DEFAULT_CONTROL_PORT,
) -> AgentRuntime:
    """Load seed config, start worker + control API, install trace hooks."""
    registry = BreakpointRegistry()
    load_breakpoints_yaml(breakpoints_path, registry)

    capture_queue = create_capture_queue()
    worker = SnapshotWorker(
        capture_queue,
        registry,
        output_dir=snapshots_dir,
    )
    worker.start()

    tracer = Tracer(registry, capture_queue)
    installer = install_trace(tracer.global_trace)

    control_server = AgentControlServer(
        registry,
        host=control_host,
        port=control_port,
    )
    control_server.start()

    return AgentRuntime(
        registry=registry,
        capture_queue=capture_queue,
        worker=worker,
        tracer=tracer,
        control_server=control_server,
        installer=installer,
    )


def run(
    *,
    target_host: str | None = None,
    target_port: int | None = None,
    control_host: str | None = None,
    control_port: int | None = None,
    breakpoints_path: Path | str | None = None,
    snapshots_dir: Path | str | None = None,
) -> None:
    """Start agent stack, then block serving the calculator on :8080."""
    from target.server import DEFAULT_HOST, DEFAULT_PORT, create_server

    runtime = start_agent(
        breakpoints_path=breakpoints_path or DEFAULT_BREAKPOINTS_PATH,
        snapshots_dir=snapshots_dir or DEFAULT_SNAPSHOTS_DIR,
        control_host=control_host or DEFAULT_CONTROL_HOST,
        control_port=control_port if control_port is not None else DEFAULT_CONTROL_PORT,
    )
    server: _CalculatorHTTPServer = create_server(
        host=target_host or DEFAULT_HOST,
        port=target_port if target_port is not None else DEFAULT_PORT,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        runtime.shutdown()


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    return int(raw) if raw else default


def main() -> None:
    run(
        target_host=os.environ.get("TARGET_HOST", "").strip() or None,
        target_port=_env_int("TARGET_PORT", 8080),
        control_host=os.environ.get("CONTROL_HOST", "").strip() or None,
        control_port=_env_int("CONTROL_PORT", DEFAULT_CONTROL_PORT),
        breakpoints_path=os.environ.get("BREAKPOINTS_YAML", "").strip() or None,
        snapshots_dir=os.environ.get("SNAPSHOTS_DIR", "").strip() or None,
    )


if __name__ == "__main__":
    main()
