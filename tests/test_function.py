import pytest

from mini_agno.tools.function import Function


def test_function_rejects_untyped_param():
    def foo(a: int, b) -> int:
        return a + b

    with pytest.raises(ValueError):
        Function(entrypoint=foo)
