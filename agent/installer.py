"""Install and remove sys.settrace + threading.settrace hooks (R15)."""

from __future__ import annotations

import sys
import threading
import types
from collections.abc import Callable
from typing import Any

TraceFunction = Callable[
    [types.FrameType, str, Any],
    "TraceFunction | None",
]


class TraceInstaller:
    """Manage process-wide trace hooks for the main thread and new threads."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._installed = False
        self._trace_fn: TraceFunction | None = None

    @property
    def is_installed(self) -> bool:
        with self._lock:
            return self._installed

    @property
    def trace_function(self) -> TraceFunction | None:
        with self._lock:
            return self._trace_fn

    def install(self, trace_fn: TraceFunction) -> None:
        if trace_fn is None:
            raise ValueError("trace_fn must not be None")
        with self._lock:
            sys.settrace(trace_fn)
            threading.settrace(trace_fn)
            self._trace_fn = trace_fn
            self._installed = True

    def remove(self) -> None:
        with self._lock:
            sys.settrace(None)
            threading.settrace(None)
            self._trace_fn = None
            self._installed = False


def install_trace(trace_fn: TraceFunction) -> TraceInstaller:
    """Install tracing on ``sys`` and ``threading``; return the installer handle."""
    installer = TraceInstaller()
    installer.install(trace_fn)
    return installer


def remove_trace(installer: TraceInstaller) -> None:
    """Remove tracing installed by ``install_trace``."""
    installer.remove()


def disable_tracing_on_current_thread() -> None:
    """Agent-owned threads must not inherit target tracing (§5.11, R24)."""
    sys.settrace(None)
    threading.settrace(None)
