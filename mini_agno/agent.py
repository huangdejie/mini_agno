from dataclasses import dataclass, field
from typing import Any
from mini_agno.models.base import Model
from mini_agno.models.message import Message, ModelResponse, ToolCall
from mini_agno.session import Session
from mini_agno.tools.function import Function, FunctionCall
import json


@dataclass
class Agent:
    model: Model
    tools: list[Function]
    max_iterations: int = 10
    output_schema: type | None = None  # 传Weather这种Pydantic类，不传就是自由文本
    sessions: dict[str,Session] = field(default_factory=dict)

    def _find_tool_call(self, tool_call: ToolCall) -> Function:
        for tool in self.tools:
            if tool.name == tool_call.name:
                return tool
        return None
    
    def _get_or_create_session(self, session_id: str) -> Session:
        if session_id not in self.sessions:
            self.sessions[session_id] = Session(session_id=session_id)
        return self.sessions[session_id]

    def run(self, user_message: str, session_id: str = "default") -> Any:
        iteration = 0
        user_msg = Message(role="user", content=user_message)
        session = self._get_or_create_session(session_id)
        session.messages.append(user_msg)
        while True:
            iteration += 1
            if iteration > self.max_iterations:
                raise RuntimeError("Max iterations reached")
            resp = self.model.invoke(
                messages=session.messages, tools=[t.to_dict() for t in self.tools]
            )
            # 先记录“助手决定调用这些工具”
            session.messages.append(
                Message(
                    role="assistant",
                    content=resp.content or "",
                    tool_calls=resp.tool_calls,
                )
            )
            if resp.tool_calls:
                for tool_call in resp.tool_calls:
                    func = self._find_tool_call(tool_call)
                    if func is None:
                        session.messages.append(
                            Message(
                                role="tool",
                                content=f"Error: Tool {tool_call.name} not found",
                                tool_call_id=tool_call.id,
                            )
                        )
                        continue
                    func_call = FunctionCall(func, tool_call.arguments)
                    try:
                        func_result = func_call.execute()
                    except Exception as e:
                        func_result = f"Error executing {tool_call.name}: {e}"
                    session.messages.append(
                        Message(
                            role="tool",
                            content=json.dumps(func_result, default=str),
                            tool_call_id=tool_call.id,
                        )
                    )
            else:
                # 如果有输出结构，则进行结构化输出
                if self.output_schema is not None:
                    return self.output_schema.model_validate_json(resp.content)
                return resp.content
