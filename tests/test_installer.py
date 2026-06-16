import sys
import threading

from agent.installer import TraceInstaller, install_trace, remove_trace


def test_install_sets_sys_and_threading_trace():
    events: list[str] = []

    def tracer(frame, event, arg):
        events.append(event)
        return tracer

    installer = install_trace(tracer)
    try:
        assert sys.gettrace() is tracer
        assert threading.gettrace() is tracer
        assert installer.is_installed
        assert installer.trace_function is tracer

        def target() -> None:
            pass

        target()
        assert "call" in events
    finally:
        remove_trace(installer)


def test_remove_clears_trace_hooks():
    def tracer(frame, event, arg):
        return tracer

    installer = install_trace(tracer)
    remove_trace(installer)

    assert sys.gettrace() is None
    assert threading.gettrace() is None
    assert not installer.is_installed
    assert installer.trace_function is None


def test_remove_is_idempotent():
    installer = TraceInstaller()
    installer.install(lambda frame, event, arg: None)
    installer.remove()
    installer.remove()
    assert sys.gettrace() is None
    assert threading.gettrace() is None


def test_install_rejects_none():
    installer = TraceInstaller()
    try:
        installer.install(None)  # type: ignore[arg-type]
        raised = False
    except ValueError:
        raised = True
    assert raised
    assert not installer.is_installed


def test_threading_settrace_applies_to_new_threads():
    events: list[tuple[str, str]] = []
    lock = threading.Lock()

    def tracer(frame, event, arg):
        if event == "call" and frame.f_code.co_name == "worker_target":
            with lock:
                events.append((threading.current_thread().name, event))
        return tracer

    installer = install_trace(tracer)
    try:

        def worker_target() -> None:
            pass

        thread = threading.Thread(target=worker_target, name="calc-thread")
        thread.start()
        thread.join()

        assert ("calc-thread", "call") in events
    finally:
        remove_trace(installer)


def test_reinstall_replaces_trace_function():
    first_calls: list[str] = []
    second_calls: list[str] = []

    def first(frame, event, arg):
        first_calls.append(event)
        return first

    def second(frame, event, arg):
        second_calls.append(event)
        return second

    installer = TraceInstaller()
    installer.install(first)

    def run_once() -> None:
        pass

    run_once()
    assert first_calls
    assert not second_calls

    installer.install(second)
    assert sys.gettrace() is second
    assert threading.gettrace() is second

    run_once()
    assert second_calls
    installer.remove()
