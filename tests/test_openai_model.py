"""OpenAIModel 的转换逻辑测试（纯 mock，不打真 API）。

为什么不测真 API：
- 真模型请求需要 DEEPSEEK_API_KEY、会花钱、CI/无网环境会失败。
- 这里只验证「mini-agno Message ⟷ OpenAI SDK dict」的翻译逻辑，
  这层逻辑出错的概率最高（role 分流、content 为 None、arguments dumps/loads 方向）。
- 真模型端到端验证靠 `uv run python examples/run_bake_demo.py` 手动跑。
"""

import json
from unittest.mock import MagicMock

from mini_agno.models.message import Message, ToolCall
from mini_agno.models.openai_model import OpenAIModel

# OpenAI() 在 __init__ 就校验 key，key 为空直接抛错；
# 这里只是构造实例来测转换逻辑，给个假 key 即可。
_FAKE_KEY = "fake-key-for-test"


def _make_model() -> OpenAIModel:
    import os

    os.environ["DEEPSEEK_API_KEY"] = _FAKE_KEY
    return OpenAIModel()


def _stub_client(model: OpenAIModel, *, content, tool_calls=None):
    """把 model.client.chat.completions.create 替换成返回假响应的 stub。"""
    fake = MagicMock()
    fake.choices = [
        MagicMock(message=MagicMock(content=content, tool_calls=tool_calls))
    ]
    model.client.chat.completions.create = MagicMock(return_value=fake)
    return model.client.chat.completions.create


def test_message_to_openai_dict_tool_result():
    """role=tool 的工具结果消息：必须带 tool_call_id，不夹带 tool_calls。"""
    m = _make_model()
    d = m._message_to_openai_dict(
        Message(role="tool", content="42", tool_call_id="call_1")
    )
    assert d == {"role": "tool", "content": "42", "tool_call_id": "call_1"}


def test_message_to_openai_dict_assistant_with_tools():
    """assistant 带工具调用：content 为 None 时该 key 不出现。"""
    m = _make_model()
    d = m._message_to_openai_dict(
        Message(
            role="assistant",
            content=None,
            tool_calls=[ToolCall(id="call_1", name="add", arguments={"a": 1})],
        )
    )
    assert "content" not in d  # None 不能放进去
    assert d["tool_calls"] == [
        {
            "id": "call_1",
            "type": "function",
            "function": {
                "name": "add",
                "arguments": json.dumps({"a": 1}),
            },
        }
    ]


def test_message_to_openai_dict_plain_user():
    """普通 user 消息：只有 role + content。"""
    m = _make_model()
    d = m._message_to_openai_dict(Message(role="user", content="hi"))
    assert d == {"role": "user", "content": "hi"}


def test_invoke_plain_text():
    """入站：模型返回纯文本 → ModelResponse(content=..., tool_calls=[])。"""
    m = _make_model()
    _stub_client(m, content="hello", tool_calls=None)
    r = m.invoke([Message(role="user", content="中国的首都哪里")])
    assert r.content == "hello"
    assert r.tool_calls == []


def test_invoke_with_tool_calls():
    """入站：模型返回 tool_calls，arguments 是 JSON 字符串 → 解析成 dict。"""
    m = _make_model()

    fn = MagicMock()
    fn.configure_mock(name="add", arguments=json.dumps({"a": 1, "b": 2}))
    tc = MagicMock()
    tc.configure_mock(id="call_1", function=fn)

    _stub_client(m, content=None, tool_calls=[tc])
    r = m.invoke([Message(role="user", content="1+2")])

    assert r.content is None
    assert r.tool_calls[0].id == "call_1"
    assert r.tool_calls[0].name == "add"
    assert r.tool_calls[0].arguments == {"a": 1, "b": 2}  # 字符串 → dict
