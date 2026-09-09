from dataclasses import dataclass
from typing import Callable, override
from mini_agno.workflow.step import Step

@dataclass(kw_only=True)
class Condition(Step):
    condition: Callable[[str],bool]
    then_steps: list[Step]
    else_steps: list[Step]

    def __post_init__(self):
        if self.condition is None:
            raise ValueError("Condition must have a condition callable")
        if self.then_steps is None:
            raise ValueError("Condition must have then_steps")
        if self.else_steps is None:
            raise ValueError("Condition must have else_steps")

    @override   
    def run(self, input: str) -> str:
        if self.condition(input):
            for step in self.then_steps:
                input = step.run(input)
        else:
            for step in self.else_steps:
                input = step.run(input)
        return input
