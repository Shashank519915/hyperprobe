from urllib.parse import parse_qs

from target.services.math_service import MathService


class RouteHandler:
    """Layer 1 — /calculate query parsing and MathService delegation."""

    def __init__(self, math_service: MathService | None = None) -> None:
        self._math_service = math_service or MathService()

    def handle_calculate(self, query_string: str) -> dict[str, float | str]:
        op, a, b = self.parse_calculate_query(query_string)
        result = self._math_service.compute(op, a, b)
        return {"op": op, "a": a, "b": b, "result": result}

    @staticmethod
    def parse_calculate_query(query_string: str) -> tuple[str, float, float]:
        params = parse_qs(query_string, keep_blank_values=False)
        op = _single_param(params, "op")
        a = _parse_float(_single_param(params, "a"), "a")
        b = _parse_float(_single_param(params, "b"), "b")
        return op, a, b


def _single_param(params: dict[str, list[str]], name: str) -> str:
    values = params.get(name)
    if not values:
        raise ValueError(f"missing parameter: {name}")
    return values[0]


def _parse_float(raw: str, name: str) -> float:
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"invalid numeric parameter: {name}") from exc
