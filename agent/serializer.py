import inspect
import types
from typing import Any


class SafeSerializer:
    """Defensive JSON-oriented serialization for captured locals (ARCHITECTURE_V2 §5.9)."""

    def __init__(self, max_depth: int = 5) -> None:
        self.max_depth = max_depth

    def serialize_locals(self, locals_dict: dict[str, Any]) -> dict[str, Any]:
        try:
            return {key: self.serialize(value) for key, value in locals_dict.items()}
        except Exception as exc:  # pragma: no cover — serialize should not raise
            return {"serialization_error": str(exc)}

    def serialize(
        self,
        value: Any,
        *,
        _depth: int = 0,
        _seen: set[int] | None = None,
    ) -> Any:
        if _seen is None:
            _seen = set()

        if _depth > self.max_depth:
            return "<max_depth>"

        if value is None or isinstance(value, (bool, int, float, str)):
            return value

        if isinstance(value, (types.FunctionType, types.MethodType, types.BuiltinFunctionType)):
            return self._format_callable(value)

        if inspect.isgenerator(value) or inspect.isasyncgen(value):
            return "<generator>"

        if isinstance(value, bytes):
            preview = value[:32]
            suffix = "..." if len(value) > 32 else ""
            return f"<bytes len={len(value)} {preview!r}{suffix}>"

        if isinstance(value, bytearray):
            return f"<bytearray len={len(value)}>"

        obj_id = id(value)
        if obj_id in _seen:
            return "<circular>"

        if isinstance(value, dict):
            _seen.add(obj_id)
            return {
                str(key): self.serialize(
                    item, _depth=_depth + 1, _seen=_seen
                )
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple, set, frozenset)):
            _seen.add(obj_id)
            return [
                self.serialize(item, _depth=_depth + 1, _seen=_seen)
                for item in value
            ]

        _seen.add(obj_id)
        try:
            return repr(value)
        except Exception:
            return f"<unserializable {type(value).__qualname__}>"

    @staticmethod
    def _format_callable(value: Any) -> str:
        name = getattr(value, "__qualname__", None) or getattr(
            value, "__name__", type(value).__qualname__
        )
        return f"<callable {name}>"
