"""Shared pytest fixtures for HyperProbe tests."""


def pytest_sessionfinish(session, exitstatus):
    """Scaffold phase: no test modules yet — exit 0 instead of pytest's code 5."""
    if exitstatus == 5:
        session.exitstatus = 0
