from mini_agno.tools.function import Function, FunctionCall


def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b


def test_add_schema():
    func = Function(entrypoint=add)
    print(func.to_dict())
    assert func.to_dict() == {
        "name": "add",
        "description": "Add two numbers together",
        "parameters": {
            "type": "object",
            "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
            "required": ["a", "b"],
        },
    }


def test_function_execute():
    func = Function(entrypoint=add)
    funcallable = FunctionCall(function=func, arguments={"a": 1, "b": 2})
    assert funcallable.execute() == 3


def init_num():
    return 0


def test_function_call_none_param_execute():
    func = Function(entrypoint=init_num)
    funcallable = FunctionCall(function=func, arguments={})
    assert funcallable.execute() == 0
