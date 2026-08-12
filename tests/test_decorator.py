from mini_agno.tools.decorator import tool
from mini_agno.tools.function import Function, FunctionCall


@tool
def add(a: int, b: int) -> int:
    return a + b


def test_add():
    assert isinstance(add, Function)


def test_add_execute():
    function_call = FunctionCall(add, {"a": 1, "b": 2})
    assert function_call.execute() == 3
