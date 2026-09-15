import asyncio
from mini_agno.models.message import Message, ModelResponse, ToolCall
from mini_agno.models.mock import MockModel
from mini_agno.models.stream import ToolCallAccumulator


def test_accumulator_single_tool():
    acc = ToolCallAccumulator()
    acc.add_fragment(
        index=0,
        id="call_00_G3ERj90IgZpCa8yjbm343231",
        name="query_temperature",
        arguments="",
    )
    acc.add_fragment(index=0, id=None, name=None, arguments="{")
    acc.add_fragment(index=0, id=None, name=None, arguments='"')
    acc.add_fragment(index=0, id=None, name=None, arguments="b")
    acc.add_fragment(index=0, id=None, name=None, arguments="ake")
    acc.add_fragment(index=0, id=None, name=None, arguments="_")
    acc.add_fragment(index=0, id=None, name=None, arguments="house")
    acc.add_fragment(index=0, id=None, name=None, arguments='"')
    acc.add_fragment(index=0, id=None, name=None, arguments=": ")
    acc.add_fragment(index=0, id=None, name=None, arguments='"')
    acc.add_fragment(index=0, id=None, name=None, arguments="001")
    acc.add_fragment(index=0, id=None, name=None, arguments='"')
    acc.add_fragment(index=0, id=None, name=None, arguments="}")
    calls = acc.finalize()
    assert len(calls) == 1
    assert calls[0].id == "call_00_G3ERj90IgZpCa8yjbm343231"
    assert calls[0].name == "query_temperature"
    assert calls[0].arguments == {"bake_house": "001"}


def test_accumulator_first_fragment_has_arguments():  # 首片 arguments 非空的分支
    acc = ToolCallAccumulator()
    acc.add_fragment(index=0, id="c2", name="query", arguments='{"city":')  # 非空首片！
    acc.add_fragment(index=0, id=None, name=None, arguments=' "北京"}')
    calls = acc.finalize()
    assert calls[0].arguments == {"city": "北京"}


def test_accumulator_two_tools():  # 双桶互不污染
    acc = ToolCallAccumulator()
    acc.add_fragment(index=0, id="t1", name="query_temperature", arguments="")
    acc.add_fragment(index=0, id=None, name=None, arguments='{"bake_house": "001"}')
    acc.add_fragment(index=1, id="h1", name="query_humidity", arguments="")
    acc.add_fragment(index=1, id=None, name=None, arguments='{"bake_house": "001"}')
    calls = acc.finalize()
    assert [c.name for c in calls] == ["query_temperature", "query_humidity"]
    assert all(c.arguments == {"bake_house": "001"} for c in calls)


def test_accumulator_empty():
    assert ToolCallAccumulator().finalize() == []


def test_accumulator_no_arg_tool():  # 无参工具：arguments 全程空串 -> 空 dict
    acc = ToolCallAccumulator()
    acc.add_fragment(index=0, id="c3", name="get_current_time", arguments="")
    calls = acc.finalize()
    assert len(calls) == 1
    assert calls[0].name == "get_current_time"
    assert calls[0].arguments == {}


def test_mock_stream():
    async def collect():
        model = MockModel(
            id="m",
            response_list=[
                ModelResponse(content="今天天气不错适合出门"),
                ModelResponse(
                    tool_calls=[
                        ToolCall(id="c1", name="query", arguments={"city": "北京"})
                    ]
                ),
            ],
        )
        out = []
        async for r in model.ainvoke_stream(
            messages=[Message(role="user", content="今天天气怎么样")]
        ):
            out.append(r)
        async for r in model.ainvoke_stream(
            messages=[Message(role="user", content="今天天气怎么样")]
        ):
            out.append(r)
        return out

    out = asyncio.run(collect())
    print(out)
    assert "".join(r.content for r in out if r.content) == "今天天气不错适合出门"
    tool_calls = [r.tool_calls for r in out if r.tool_calls]
    print(tool_calls[0])
    assert len(tool_calls) == 1
    calls = tool_calls[0]
    assert calls[0].arguments == {"city": "北京"}
