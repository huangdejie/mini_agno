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
            k: {"type": type_map[v]} for k, v in type_hints.items() if k != "return"
        }
        self.parameters = {
            "type": "object",
            "properties": properties,
            "required": self._get_required_params(),
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
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


@dataclass
class FunctionCall:
    function: Function
    arguments: dict

    def execute(self) -> Any:
        return self.function.entrypoint(**self.arguments)
