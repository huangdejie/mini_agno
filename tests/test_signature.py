"""
Signature学习
是python中 insect 模块中一个用于表示函数调用签名(即函数的输入和输出定义)的工具。
主要服务于代码内省(Introspection),让开发者能够在代码中分析和操作函数信息，并不改变函数本身
"""

from inspect import signature, Parameter
from typing import get_type_hints


def greet(name, aget=18):
    return f"{name} is {age} years old"


sign = signature(greet)
print(sign)  # 输出: (name, age=18)

for name, param in sign.parameters.items():
    print(f"参数名:{name}")
    print(f"\t是否有默认值:{param.default != Parameter.empty}")
    print(
        f"\t默认值是什么:{param.default if param.default != Parameter.empty else '无'}"
    )


# 调用函数
bound = sign.bind("Alice", 19)
print(bound.arguments)

"""检查参数是否必须"""


def my_function(x, b=20, c=20):
    pass


sig = signature(my_function)
for name, param in sig.parameters.items():
    if param.default == Parameter.empty:
        print(f"{name} 是必须的参数")
    else:
        print(f"{name} 不是必须的参数")


"""参数检查装饰器"""


def check_types(func):
    si = signature(func)

    def wrapper(*args, **kwargs):
        bound_args = si.bind(*args, **kwargs)
        bound_args.apply_defaults()
        print(f"调用{func.__name__}，参数如下:")
        for name, value in bound_args.arguments.items():
            print(f"\t{name}={value}")
        return func(*args, **kwargs)

    return wrapper


@check_types
def calculate(a: int, b=5, c=10) -> int:
    return a + b + c


print(calculate(1, c=3))


print("******")


def reduce(a: int, b: int, c=12) -> int:
    return a - b


s = signature(reduce)
for name, param in s.parameters.items():
    if param.default == Parameter.empty:
        print(f"{name} 是必须的参数")
    else:
        print(f"{name} 不是必须的参数")
    print(f"{name}->{param}")

print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")


t = get_type_hints(reduce)
for name, param in s.parameters.items():
    print(f"{param}")

types_map = {int: "integer", str: "string", float: "number", bool: "boolean"}
paramenters = {}
for name, type_hint in t.items():
    paramenters[name] = types_map.get(type_hint, "unknown")
print(paramenters)
