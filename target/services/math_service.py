from target.engines.addition import AdditionEngine
from target.engines.division import DivisionEngine
from target.engines.multiplication import MultiplicationEngine
from target.engines.subtraction import SubtractionEngine


class MathService:
    """Layer 2 service — routes operations to layer-3 engines."""

    def __init__(self) -> None:
        self._addition = AdditionEngine()
        self._subtraction = SubtractionEngine()
        self._multiplication = MultiplicationEngine()
        self._division = DivisionEngine()

    def compute(self, op: str, a: float, b: float) -> float:
        match op:
            case "add":
                return self._addition.add(a, b)
            case "sub":
                return self._subtraction.subtract(a, b)
            case "mul":
                return self._multiplication.multiply(a, b)
            case "div":
                return self._division.divide(a, b)
            case _:
                raise ValueError(f"unsupported operation: {op!r}")
