from mini_agno.agent import Agent
from mini_agno.models.message import ModelResponse
from mini_agno.models.mock import MockModel
from mini_agno.team.team import Team
import pytest


def test_team_sequential():
    a1 = Agent(
        model=MockModel(
            id="sum",
            response_list=[
                ModelResponse(content="总结：输入很重要"),
            ],
        ),
        tools=[],
    )
    a2 = Agent(
        model=MockModel(
            id="polish",
            response_list=[
                ModelResponse(content="[润色版] 输入非常重要"),
            ],
        ),
        tools=[],
    )
    team = Team(members=[a1, a2], mode="sequential")
    result = team.run("请处理这段输入")
    assert result == "[润色版] 输入非常重要"
    # 验证 a1 的输出确实作为 a2 的输入
    assert a2.sessions["default"].messages[0].role == "user"
    assert a2.sessions["default"].messages[0].content == "总结：输入很重要"


def test_team_rejects_unsupported_mode():
    a2 = Agent(
        model=MockModel(
            id="polish",
            response_list=[
                ModelResponse(content="[润色版] 输入非常重要"),
            ],
        ),
        tools=[],
    )
    with pytest.raises(ValueError, match="Invalid mode"):
        Team(members=[a2], mode="parallel")


def test_team_requires_at_least_one_member():
    with pytest.raises(ValueError, match="at least one member"):
        Team(members=[], mode="sequential")
