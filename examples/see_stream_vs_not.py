"""探针：亲眼看流式和非流式的差别。

跑法：uv run python examples/see_stream_vs_not.py
三段：
  1) 非流式 + 文本回答：等全部生成完，一次拿到一个完整对象
  2) 流式 + 文本回答：chunk 一个一个到，content 是碎片
  3) 流式 + 工具调用：tool_call 的 arguments 被剁碎陆续到（accumulator 要解决的问题）
"""

import asyncio
import time

from os import getenv

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

client = AsyncOpenAI(base_url="https://api.deepseek.com", api_key=getenv("DEEPSEEK_API_KEY"))
MODEL = "deepseek-chat"


async def part1_non_stream_text():
    print("=" * 60)
    print("第 1 段：非流式 + 文本 —— 等到底，一次拿到")
    print("=" * 60)
    t0 = time.time()
    resp = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "用30个字介绍一下你自己"}],
    )
    elapsed = time.time() - t0
    print(f"等待 {elapsed:.2f} 秒后，一次性返回了 1 个对象:")
    print(f"  类型: {type(resp).__name__}")
    print(f"  完整 content: {resp.choices[0].message.content!r}")
    print(f"  你在这 {elapsed:.2f} 秒里什么都看不到，拿到时已是成品\n")

async def part2_non_stream_text_tool():
    print("="*60)
    print("第 2 段：非流式 + 工具调用 —— 等到底，一次拿到")
    print("="*60)
    t0 = time.time()
    tools = [
        {
            "type": "function",
            "function": {
                "name": "query_temperature",
                "description": "查询指定烤房的当前温度",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bake_house": {"type": "string", "description": "烤房编号，如 001"}
                    },
                    "required": ["bake_house"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "query_humidity",
                "description": "查询指定烤房的当前湿度",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bake_house": {"type": "string", "description": "烤房编号，如 001"}
                    },
                    "required": ["bake_house"],
                },
            },
        }
    ]
    resp = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "查询烤房001的当前温度"}],
        tools=tools
    )
    elapsed = time.time() - t0
    msg = resp.choices[0].message
    print(f"等待 {elapsed:.2f} 秒后，一次性返回了 1 个对象:")
    print(f"  类型: {type(resp).__name__}")
    print(f"  content(工具轮经常是自言自语): {msg.content!r}")
    if msg.tool_calls:
        for tc in msg.tool_calls:
            print(f"  完整 tool_call: id={tc.id!r} name={tc.function.name!r}")
            print(f"  arguments 一次到位: {tc.function.arguments!r}")
    print(f"  你在这 {elapsed:.2f} 秒里什么都看不到，拿到时已是成品\n")


async def part3_stream_text():
    print("=" * 60)
    print("第 3 段：流式 + 文本 —— chunk 陆续到，content 是碎片")
    print("=" * 60)
    t0 = time.time()
    stream = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "用30个字介绍一下你自己"}],
        stream=True,
    )
    chunks = 0
    async for chunk in stream:
        elapsed = time.time() - t0
        if not chunk.choices:  # 最后的 usage 包
            print(f"[{elapsed:5.2f}s] 第{chunks + 1}包: 无 choices，只有 usage={chunk.usage is not None}")
            continue
        delta = chunk.choices[0].delta
        finish = chunk.choices[0].finish_reason
        if delta.content:
            chunks += 1
            print(f"[{elapsed:5.2f}s] 第{chunks}包: content={delta.content!r}")
        elif finish:
            print(f"[{elapsed:5.2f}s] 结束包: finish_reason={finish!r}")
    print(f"-- 共 {chunks} 个内容碎片，拼起来才是完整回答；每个碎片到达时间不同\n")


async def part4_stream_tool_call():
    print("=" * 60)
    print("第 4 段：流式 + 工具调用 —— arguments 被剁碎陆续到（accumulator 的战场）")
    print("=" * 60)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "query_temperature",
                "description": "查询指定烤房的当前温度",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bake_house": {"type": "string", "description": "烤房编号，如 001"}
                    },
                    "required": ["bake_house"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "query_humidity",
                "description": "查询指定烤房的当前湿度",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bake_house": {"type": "string", "description": "烤房编号，如 001"}
                    },
                    "required": ["bake_house"],
                },
            },
        }
    ]
    t0 = time.time()
    stream = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "帮我查一下001烤房的温湿度信息"}],
        tools=tools,
        stream=True,
    )
    pieces = []
    chunks = 0
    async for chunk in stream:
        elapsed = time.time() - t0
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta.content:
            chunks += 1
            print(f"[{elapsed:5.2f}s] 第{chunks}包: content={delta.content!r}")
        if delta.tool_calls:
            for tc in delta.tool_calls:
                frag_args = tc.function.arguments if tc.function else None
                print(
                    f"[{elapsed:5.2f}s] index={tc.index} id={tc.id!r} "
                    f"name={(tc.function.name if tc.function else None)!r} "
                    f"arguments碎片={frag_args!r}"
                )
                pieces.append(frag_args or "")
        if chunk.choices[0].finish_reason:
            print(f"[{time.time() - t0:5.2f}s] finish_reason={chunk.choices[0].finish_reason!r}")
    full = "".join(pieces)
    print(f"-- 拼起来的 arguments: {full!r}")
    print(f"-- 这串才等于非流式里的完整 arguments，收到任何一片单独时都是废的\n")


async def main():
    await part1_non_stream_text()
    await part2_non_stream_text_tool()
    await part3_stream_text()
    await part4_stream_tool_call()


asyncio.run(main())
