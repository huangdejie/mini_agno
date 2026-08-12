from pydantic import BaseModel


class ToolCall(BaseModel):
    id: str = "" # 模型返回的调用id
    name: str
    arguments: dict


class Message(BaseModel):
    role: str
    content: str | None = None # 可选(调工具时 assistant content 常为空)
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None # tool消息回链

class ModelResponse(BaseModel):
    content: str | None = None
    tool_calls: list[ToolCall] | None = None


class RunResponse(BaseModel):
    content: str
    messages: list[Message]
