
from dataclasses import dataclass
from typing import Callable

from mini_agno.agent import Agent


@dataclass
class Step:
    name:str | None = None
    agent:Agent | None = None
    func: Callable | None = None

    def __post_init__(self):
        if self.agent and self.func:
            raise ValueError("Step cannot have both an agent and a function")
        if self.agent is None and self.func is None:
            raise ValueError("Step must have either an agent or a function")
        if not self.name:
            self.name = self.func.__name__ if self.func else self.agent.name

    def run(self,input:str) -> str:
        if self.agent:
            return self.agent.run(input)
        elif self.func:
            return self.func(input)
        else:
            raise ValueError("Step must have either an agent or a function")
