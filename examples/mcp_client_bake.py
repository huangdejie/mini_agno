import asyncio
from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def main():
    transport = StdioTransport("uv", args=["run", "examples/mcp_server_bake.py"])
    client = Client(transport)

    async with client:
        # 获取工具清单
        tools = await client.list_tools()
        print("=== server 自报的工具 ===")
        for t in tools:
            print(f"name: {t.name}")
            print(f"description: {t.description}")
            print(f"input_schema: {t.input_schema}")
            print()

        # ② 手动执行：把一次工具调用转发给 server
        result = await client.call_tool("query_temperature", {"bake_house": "001"})
        print("=== call_tool 结果 ===")
        print(result)


asyncio.run(main())
