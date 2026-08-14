from dataclasses import dataclass
from inspect import Parameter, signature
from typing import Any, Callable, Optional, get_type_hints

type_map = {int: "integer", str: "string", float: "number", bool: "boolean"}


@dataclass
class Function:
    entrypoint: Callable
    name: str = ""
    description: str = ""
    parameters: Optional[dict] = None

    def __post_init__(self):
        self.name = self.entrypoint.__name__
        self.description = self.entrypoint.__doc__ or ""
        type_hints = get_type_hints(self.entrypoint)
        properties = {
            k: {"type": type_map.get(v, "string")}
            for k, v in type_hints.items()
            if k != "return"
        }
        # 获取含类型注解的参数定义，去除返回参数,没有类型参数的不包含在这里面
        hint_names = set(type_hints) - {"return"}
        # 获取所有参数名
        all_params = set(signature(self.entrypoint).parameters)  # 所有参数名
        # 获取没有类型注解的参数名
        no_hint = [p for p in all_params if p not in hint_names]  # 没注解的
        if no_hint:
            # 如果有参数没有类型注解，则报错
            raise ValueError(
                f"工具 '{self.name}' 的参数缺少类型注解: {no_hint}。"
                f"请给每个参数加类型注解（如 def {self.name}(x: int)），模型才能正确调用。"
            )
        self.parameters = {
            "type": "object",
            "properties": properties,
            "required": [p for p in self._get_required_params() if p in hint_names],
        }

    def _get_required_params(self) -> list:
        sig = signature(self.entrypoint)
        required_params = []
        for param_name, param in sig.parameters.items():
            if param.default == Parameter.empty:
                required_params.append(param_name)
        return required_params

    def to_dict(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass
class FunctionCall:
    function: Function
    arguments: dict

    def execute(self) -> Any:
        return self.function.entrypoint(**self.arguments)
