from mini_agno.agent import Agent
from mini_agno.models.mock import MockModel
from mini_agno.models.message import ModelResponse


def test_agent_remembers_history():
    mock = MockModel(
        id="mock",
        response_list=[
            ModelResponse(content="你好张三"),
            ModelResponse(content="你好李四,你擅长Java"),
        ],
    )
    agent = Agent(model=mock, tools=[])
    resp = agent.run("我叫张三")
    print(resp)
    agent.run("我擅长什么语言开发")
    print(len(agent.messages))
    print(agent.messages)
    assert len(agent.messages) == 4
    assert agent.messages[0].content == "我叫张三"
    assert agent.messages[1].content == "你好张三"


def test_messages_default_not_shared():
    """两个 Agent 实例不能共享同一个 messages 列表"""
    a1 = Agent(model=MockModel(id="m1", response_list=[]), tools=[])
    a2 = Agent(model=MockModel(id="m2", response_list=[]), tools=[])
    assert a1.messages is not a2.messages
