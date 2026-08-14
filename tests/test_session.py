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
    print(len(agent.sessions['default'].messages))
    print(agent.sessions['default'].messages)
    assert len(agent.sessions['default'].messages) == 4
    assert agent.sessions['default'].messages[0].content == "我叫张三"
    assert agent.sessions['default'].messages[1].content == "你好张三"


def test_messages_default_not_shared():
    """两个 Agent 实例不能共享同一个 messages 列表"""
    a1 = Agent(model=MockModel(id="m1", response_list=[ModelResponse(content="你好张三")]), tools=[])
    a1.run("我叫张三")
    a2 = Agent(model=MockModel(id="m2", response_list=[ModelResponse(content="你叫李四")]), tools=[])
    a2.run("我叫什么")
    print(a1.sessions['default'].messages)
    assert a1.sessions['default'].messages is not a2.sessions['default'].messages


def test_multi_session_isolated():
    """同一个 Agent 实例在不同会话之间是隔离的"""
    mock = MockModel(id="mock", response_list=[ModelResponse(content="记住张三"),
                                               ModelResponse(content="记住李四"),
                                               ModelResponse(content="你叫张三")])

    agent = Agent(model=mock, tools=[])
    agent.run("我叫张三", session_id="s1")
    agent.run("我叫李四", session_id="s2")
    agent.run("我叫什么", session_id="s1")

    assert len(agent.sessions['s1'].messages) == 4
    assert len(agent.sessions['s2'].messages) == 2
    assert agent.sessions['s1'].messages[0].content == "我叫张三"
    assert agent.sessions['s1'].messages[3].content == "你叫张三"
