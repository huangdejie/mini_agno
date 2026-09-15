from dataclasses import dataclass, field

from mini_agno.agent import Agent
from mini_agno.models.base import Model
from mini_agno.tools.function import Function


@dataclass
class Team:
    members: list[Agent]
    mode: str = "sequential"  # 先只支持顺序模式
    leader_model: Model | None = None
    leader: Agent = field(
        init=False
    )  # coordinate 时在 __post_init__ 中初始化,不需要显式传入

    def __post_init__(self):
        if not self.members:
            raise ValueError("Team must have at least one member")
        for member in self.members:
            if not isinstance(member, Agent):
                raise ValueError("All members must be instances of Agent")
        if self.mode == "sequential":
            pass
        elif self.mode == "coordinate":
            self._validate_coordinate()
            self.leader = Agent(
                model=self.leader_model,
                tools=[self._make_delegate_tool()],
                instructions=self._build_leader_instructions(),
            )
        else:
            raise ValueError(f"Invalid mode: {self.mode}")

    def _validate_coordinate(self):
        if self.leader_model is None:
            raise ValueError("coordinate mode must have a leader model")
        names = []
        for m in self.members:
            if not m.name:
                raise ValueError("All members must have a name")
            if not m.description:
                raise ValueError(
                    f"coordinate mode: member '{m.name}' must have a description"
                )
            names.append(m.name)
        if len(names) != len(set(names)):
            raise ValueError("All members must have a unique name")

    def _make_delegate_tool(self) -> Function:
        members_by_name = {m.name: m for m in self.members}

        def delegate_task_to_member(member_id: str, task: str) -> str:
            """把任务委派给某个团队成员，返回该成员的执行结果
            Args:
                member_id:成员的名字（必须是团队成员之一）
                task:要交给这个成员完成的任务描述
            Returns:
                str:团队中被委派成员的执行结果
            """
            member = members_by_name.get(member_id)
            return member.run(task)

        return Function(entrypoint=delegate_task_to_member)

    def _build_leader_instructions(self) -> str:
        lines = [
            "你是一个团队 Leader，负责把任务委派给合适的团队成员，并汇总他们的结果。",
            "团队成员如下:",
        ]
        for m in self.members:
            lines.append(f"- {m.name}: {m.description}")
        lines.append(
            "使用 `delegate_task_to_member(member_id, task)` 委派任务。委派后根据结果决定下一步，最终给出完整回答。"
        )
        return "\n".join(lines)

    def run(self, message: str) -> str:
        current = message
        if self.mode == "sequential":
            for agent in self.members:
                current = agent.run(current)
        elif self.mode == "coordinate":
            current = self.leader.run(current)
        return current
