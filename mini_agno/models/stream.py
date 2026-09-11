import json
from mini_agno.models.message import ToolCall


class ToolCallAccumulator:
    """把流式到达的 tool_call 按 index 分桶，拼装成完整的 ToolCall。
    eg:
        index=0 id='call_00_G3ERj90IgZpCa8yjbm343231' name='query_temperature' arguments=''
        index=0 id=None name=None arguments='{'
        index=0 id=None name=None arguments='"'
        index=0 id=None name=None arguments='b'
        index=0 id=None name=None arguments='ake'
        index=0 id=None name=None arguments='_'
        index=0 id=None name=None arguments='house'
        index=0 id=None name=None arguments='"'
        index=0 id=None name=None arguments=': '
        index=0 id=None name=None arguments='"'
        index=0 id=None name=None arguments='001'
        index=0 id=None name=None arguments='"'
        index=0 id=None name=None arguments='}'
    """

    def __init__(self):
        # index -> {"id":...,"name":...., "arguments":越拼越长的字符串}
        self._buckets: dict[int, dict] = {}

    def add_fragment(
        self, index: int, id: str | None, name: str | None, arguments: str | None
    ) -> None:
        if index not in self._buckets:
            self._buckets[index] = {
                "id": id or "",
                "name": name or "",
                "arguments": arguments or "",
            }
        else:
            bucket = self._buckets[index]
            if id:
                bucket["id"] = id
            if name:
                bucket["name"] = name
            if arguments:
                # 追加
                bucket["arguments"] += arguments

    def finalize(self) -> list[ToolCall]:
        tool_calls = []
        for index in sorted(self._buckets):   # 按 index 升序，不依赖碎片的到达顺序
            value = self._buckets[index]
            tool_call = ToolCall(
                id=value["id"],
                name=value["name"],
                # 无参工具的 arguments 可能全程为空串，兜成 "{}" 才能过 json.loads
                arguments=json.loads(value["arguments"] or "{}"),
            )
            tool_calls.append(tool_call)
        return tool_calls
