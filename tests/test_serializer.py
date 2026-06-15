from agent.serializer import SafeSerializer


def test_serializes_primitives():
    serializer = SafeSerializer()
    assert serializer.serialize(42) == 42
    assert serializer.serialize("hello") == "hello"
    assert serializer.serialize(None) is None
    assert serializer.serialize(True) is True


def test_serializes_bytes_with_length_and_preview():
    serializer = SafeSerializer()
    result = serializer.serialize(b"abc")
    assert result == "<bytes len=3 b'abc'>"


def test_serializes_callable_without_raising():
    serializer = SafeSerializer()

    def helper():
        return 1

    result = serializer.serialize(helper)
    assert result.startswith("<callable ")
    assert "helper" in result


def test_serializes_generator_without_raising():
    serializer = SafeSerializer()

    def gen():
        yield 1

    result = serializer.serialize(gen())
    assert result == "<generator>"


def test_serializes_circular_dict():
    serializer = SafeSerializer()
    circular: dict[str, object] = {"a": 1}
    circular["self"] = circular

    result = serializer.serialize(circular)
    assert result["a"] == 1
    assert result["self"] == "<circular>"


def test_depth_limit_truncates_nested_structures():
    serializer = SafeSerializer(max_depth=2)
    nested = {"l1": {"l2": {"l3": "deep"}}}

    result = serializer.serialize(nested)
    assert result["l1"]["l2"]["l3"] == "<max_depth>"


def test_serialize_locals_never_raises_on_pathological_values():
    serializer = SafeSerializer()

    class BadRepr:
        def __repr__(self) -> str:
            raise RuntimeError("repr failed")

    locals_dict = {
        "num": 1,
        "fn": (lambda: None),
        "bad": BadRepr(),
    }
    result = serializer.serialize_locals(locals_dict)
    assert result["num"] == 1
    assert result["fn"].startswith("<callable")
    assert "BadRepr" in result["bad"]
