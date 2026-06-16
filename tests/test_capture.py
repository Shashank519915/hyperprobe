import sys
import types

from agent.capture import capture_raw, capture_stack_frames
from agent.models import RawCapture, RawFrame, TraceEvent


def _capture_from_nested_call(
    *,
    event: TraceEvent = TraceEvent.CALL,
    return_value: object | None = None,
) -> RawCapture:
    captured: list[RawCapture] = []

    def middle(m: int) -> int:
        def inner(n: int) -> int:
            frame = sys._getframe()
            captured.append(
                capture_raw(
                    frame,
                    breakpoint_id="bp-nested",
                    event=event,
                    return_value=return_value,
                    timestamp=100.0,
                    thread_id=99,
                )
            )
            return n * 2

        return inner(m)

    middle(3)
    return captured[0]


def test_capture_stack_innermost_first():
    raw = _capture_from_nested_call()
    names = [frame.function for frame in raw.frames]
    assert names[0] == "inner"
    assert "middle" in names
    assert "test_capture_stack_innermost_first" in names


def test_capture_includes_caller_locals():
    raw = _capture_from_nested_call()
    inner_frame = raw.frames[0]
    middle_frame = next(f for f in raw.frames if f.function == "middle")
    assert inner_frame.locals["n"] == 3
    assert middle_frame.locals["m"] == 3


def test_capture_stack_frames_normalizes_file_paths():
    frame = sys._getframe()
    frames = capture_stack_frames(frame)
    assert frames
    assert frames[0].file.endswith("tests\\test_capture.py") or frames[0].file.endswith(
        "tests/test_capture.py"
    )


def test_capture_call_event_has_no_return_value():
    raw = _capture_from_nested_call(event=TraceEvent.CALL, return_value=999)
    assert raw.event == TraceEvent.CALL
    assert raw.return_value is None


def test_capture_return_event_includes_return_value():
    raw = _capture_from_nested_call(
        event=TraceEvent.RETURN,
        return_value={"result": 6},
    )
    assert raw.event == TraceEvent.RETURN
    assert raw.return_value == {"result": 6}


def test_capture_sets_thread_and_timestamp():
    raw = _capture_from_nested_call()
    assert raw.thread_id == 99
    assert raw.timestamp == 100.0


def test_raw_capture_contains_only_copied_data():
    raw = _capture_from_nested_call()
    assert isinstance(raw, RawCapture)
    for frame in raw.frames:
        assert isinstance(frame, RawFrame)
        assert isinstance(frame.locals, dict)
        assert not isinstance(frame.locals, types.FrameType)


def test_capture_return_value_via_settrace():
    captured: list[RawCapture] = []

    def tracer(frame: types.FrameType, event: str, arg: object) -> object:
        if event == "return" and frame.f_code.co_name == "target_fn":
            captured.append(
                capture_raw(
                    frame,
                    breakpoint_id="bp-return",
                    event=TraceEvent.RETURN,
                    return_value=arg,
                )
            )
        return tracer

    def target_fn(value: int) -> int:
        doubled = value * 2
        return doubled

    sys.settrace(tracer)
    try:
        assert target_fn(5) == 10
    finally:
        sys.settrace(None)

    assert len(captured) == 1
    assert captured[0].return_value == 10
    assert captured[0].frames[0].function == "target_fn"
    assert captured[0].frames[0].locals["doubled"] == 10
