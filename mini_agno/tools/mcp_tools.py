from fastmcp import Client
from fastmcp.client.transports import StdioTransport

from mini_agno.tools.function import Function


class MCPTools:

    def __init__(self, command: str, args: list[str]):
        self._command = command
        self._args = args
        self._client: Client | None = None
        self._functions: list[Function] = []

    async def connect(self):
        transport = StdioTransport(self._command, args=self._args)
        self._client = Client(transport)
        await self._client.__aenter__()
        tools = await self._client.list_tools()
        for t in tools:
            self._functions.append(
                Function(
                    entrypoint=self._make_entrypoint(t.name),
                    name=t.name,
                    description=t.description,
                    parameters=t.input_schema,
                    skip_auto_schema=True,
                )
            )

    def get_functions(self) -> list[Function]:
        return self._functions

    async def disconnect(self):
        if self._client is not None:
            await self._client.__aexit__(None, None, None)

    def _make_entrypoint(self, tool_name: str):
        async def entrypoint(**kwargs):
            result = await self._client.call_tool(tool_name, kwargs)
            return result

        return entrypoint
