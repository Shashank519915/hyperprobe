import pytest

from target.engines.addition import AdditionEngine
from target.engines.division import DivisionEngine
from target.engines.multiplication import MultiplicationEngine
from target.engines.subtraction import SubtractionEngine
from target.services.math_service import MathService


def test_addition_engine_returns_sum():
    assert AdditionEngine().add(10, 20) == 30


def test_subtraction_engine_returns_difference():
    assert SubtractionEngine().subtract(10, 3) == 7


def test_multiplication_engine_returns_product():
    assert MultiplicationEngine().multiply(4, 5) == 20


def test_division_engine_returns_quotient():
    assert DivisionEngine().divide(20, 4) == 5


def test_division_engine_raises_on_zero_divisor():
    with pytest.raises(ZeroDivisionError):
        DivisionEngine().divide(10, 0)


@pytest.fixture
def math_service() -> MathService:
    return MathService()


def test_math_service_routes_add(math_service: MathService):
    assert math_service.compute("add", 10, 20) == 30


def test_math_service_routes_sub(math_service: MathService):
    assert math_service.compute("sub", 10, 3) == 7


def test_math_service_routes_mul(math_service: MathService):
    assert math_service.compute("mul", 4, 5) == 20


def test_math_service_routes_div(math_service: MathService):
    assert math_service.compute("div", 20, 4) == 5


def test_math_service_raises_on_unknown_op(math_service: MathService):
    with pytest.raises(ValueError, match="unsupported operation"):
        math_service.compute("pow", 2, 3)


def test_math_service_propagates_zero_division(math_service: MathService):
    with pytest.raises(ZeroDivisionError):
        math_service.compute("div", 10, 0)
