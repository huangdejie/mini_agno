from mini_agno.agent import Agent
from mini_agno.models.mock import MockModel
from mini_agno.models.message import ModelResponse
import uuid


def test_agent_remembers_history():
    mock = MockModel(
        id="mock",
        response_list=[
            ModelResponse(content="你好张三"),
            ModelResponse(content="你好李四,你擅长Java"),
        ],
    )
    session_id = uuid.uuid4().hex
    print(session_id)
    agent = Agent(model=mock, tools=[])
    resp = agent.run("我叫张三", session_id=session_id)
    print(resp)
    agent.run("我擅长什么语言开发", session_id=session_id)
    print(len(agent.sessions[session_id].messages))
    print(agent.sessions[session_id].messages)
    assert len(agent.sessions[session_id].messages) == 4
    assert agent.sessions[session_id].messages[0].content == "我叫张三"
    assert agent.sessions[session_id].messages[1].content == "你好张三"


def test_messages_default_not_shared():
    a1_s1 = uuid.uuid4().hex
    a2_s2 = uuid.uuid4().hex
    """两个 Agent 实例不能共享同一个 messages 列表"""
    a1 = Agent(
        model=MockModel(id="m1", response_list=[ModelResponse(content="你好张三")]),
        tools=[],
    )
    a1.run("我叫张三", session_id=a1_s1)
    a2 = Agent(
        model=MockModel(id="m2", response_list=[ModelResponse(content="你叫李四")]),
        tools=[],
    )
    a2.run("我叫什么", session_id=a2_s2)
    print(a1.sessions[a1_s1].messages)
    assert a1.sessions[a1_s1].messages is not a2.sessions[a2_s2].messages


def test_multi_session_isolated():
    """同一个 Agent 实例在不同会话之间是隔离的"""
    mock = MockModel(
        id="mock",
        response_list=[
            ModelResponse(content="记住张三"),
            ModelResponse(content="记住李四"),
            ModelResponse(content="你叫张三"),
        ],
    )

    agent = Agent(model=mock, tools=[])
    s1 = uuid.uuid4().hex
    s2 = uuid.uuid4().hex
    agent.run("我叫张三", session_id=s1)
    agent.run("我叫李四", session_id=s2)
    agent.run("我叫什么", session_id=s1)

    assert len(agent.sessions[s1].messages) == 4
    assert len(agent.sessions[s2].messages) == 2
    assert agent.sessions[s1].messages[0].content == "我叫张三"
    assert agent.sessions[s1].messages[3].content == "你叫张三"
