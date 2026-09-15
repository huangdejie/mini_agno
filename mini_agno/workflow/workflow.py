from dataclasses import dataclass
from mini_agno.workflow.step import Step


@dataclass
class Workflow:
    steps: list[Step]

    def run(self, input: str) -> str:
        current_input = input
        for step in self.steps:
            current_input = step.run(current_input)
        return current_input
