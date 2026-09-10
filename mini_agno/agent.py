from dataclasses import dataclass, field
from typing import Any
from mini_agno import knowledge
from mini_agno.db.base import BaseDb
from mini_agno.knowledge.knowledge import Knowledge
from mini_agno.memory.manager import MemoryManager
from mini_agno.models.base import Model
from mini_agno.models.message import Message, ToolCall
from mini_agno.session import Session
from mini_agno.tools.function import Function, FunctionCall
import json


@dataclass
class Agent:
    model: Model
    tools: list[Function]
    max_iterations: int = 10
    output_schema: type | None = None  # 传Weather这种Pydantic类，不传就是自由文本
    sessions: dict[str, Session] = field(default_factory=dict)
    db: BaseDb | None = None
    memory_manager: MemoryManager | None = None
    knowledge: Knowledge | None = None
    name: str | None = None
    description: str | None = None
    instructions: str | None = None # 给Agent的自定义 system 指令

    def _find_tool_call(self, tool_call: ToolCall) -> Function:
        for tool in self.tools:
            if tool.name == tool_call.name:
                return tool
        return None

    def _get_or_create_session(self, session_id: str, user_id: str) -> Session:
        """
        如果db为空,则仅在内存中存储
        """
        if session_id in self.sessions:
            return self.sessions[session_id]
        if self.db is not None:
            result = self.db.get_session(session_id)
            if result is not None:
                session = Session(**result)
                self.sessions[session_id] = session
                return session
        session = Session(session_id=session_id, user_id=user_id, messages=[])
        self.sessions[session_id] = session
        return session

    def _upsert_session(self, session: Session) -> None:
        self.sessions[session.session_id] = session
        if self.db is not None:
            self.db.upsert_session(session)

    def _prepare_message(self, user_message: str,session:Session, user_id: str = "default") -> None:
        # 在第一次的时候，如果存在自定义的system消息，则加入
        if not session.messages:
            if self.instructions:
                session.messages.append(Message(role="system", content=self.instructions))
            if self.knowledge is not None:
                docs = self.knowledge.search(user_message)
                if docs:
                    knowledge_msg = Message(
                        role="system",
                        content="请参考以下文档回答问题：\n"
                        + "\n".join(f"- {d}" for d in docs),
                    )
                    session.messages.append(knowledge_msg)

            # 如果存在记忆管理的话，则需要把记忆拼成system消息,只有第一次的时候参会加入进去
            if self.memory_manager is not None:
                memories = self.memory_manager.get_memories(user_id)
                if memories:
                    system_msg = Message(
                        role="system", content="已知用户信息:\n-" + "\n-".join(memories)
                    )
                    session.messages.append(system_msg)

        session.messages.append(Message(role="user", content=user_message))
        
    def _execute_tool_calls(self,tool_calls:list[ToolCall],session:Session) -> None:
        for tool_call in tool_calls:
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

    def run(
        self, user_message: str, session_id: str = "default", user_id: str = "default"
    ) -> Any:
        iteration = 0
        session = self._get_or_create_session(session_id, user_id)
        self._prepare_message(user_message, session, user_id)
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
                self._execute_tool_calls(resp.tool_calls, session)
            else:
                self._upsert_session(session)
                # 这里如果将大模型的回答放入memory，一旦大模型错误的，可能会有错误，所以只筛选用户输入和工具调用的
                if self.memory_manager is not None:
                    facts = self._extract_facts(
                        [m for m in session.messages if m.role in ("user", "tool")],
                        user_id,
                    )
                    self.memory_manager.add_memories(user_id, facts)
                # 如果有输出结构，则进行结构化输出
                if self.output_schema is not None:
                    return self.output_schema.model_validate_json(resp.content)
                return resp.content
    
    async def arun(
        self, user_message: str, session_id: str = "default", user_id: str = "default"
    ) -> Any:
        iteration = 0
        session = self._get_or_create_session(session_id, user_id)
        self._prepare_message(user_message, session, user_id)
        while True:
            iteration += 1
            if iteration > self.max_iterations:
                raise RuntimeError("Max iterations reached")
            resp = await self.model.ainvoke(
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
                self._execute_tool_calls(resp.tool_calls, session)
            else:
                self._upsert_session(session)
                # 这里如果将大模型的回答放入memory，一旦大模型错误的，可能会有错误，所以只筛选用户输入和工具调用的
                if self.memory_manager is not None:
                    facts = self._aextract_facts(
                        [m for m in session.messages if m.role in ("user", "tool")],
                        user_id,
                    )
                    self.memory_manager.add_memories(user_id, facts)
                # 如果有输出结构，则进行结构化输出
                if self.output_schema is not None:
                    return self.output_schema.model_validate_json(resp.content)
                return resp.content
    
    def _extract_facts(self, messages: list[Message], user_id: str) -> list[str]:
        prompt = """
        从以下对话中提取关于用户的持久事实(如姓名、偏好、背景等)。只返回事实列表，每行一条，不要调用工具，不要有多余解释。
        """
        extract_messages = [Message(role="system", content=prompt)] + messages
        # 这里让大模型自己去提炼，然后存入memory
        resp = self.model.invoke(messages=extract_messages, tools=[])
        return [line.strip("- ") for line in resp.content.split("\n") if line.strip()]

    async def _aextract_facts(self, messages: list[Message], user_id: str) -> list[str]:
        prompt = """
        从以下对话中提取关于用户的持久事实(如姓名、偏好、背景等)。只返回事实列表，每行一条，不要调用工具，不要有多余解释。
        """
        extract_messages = [Message(role="system", content=prompt)] + messages
        # 这里让大模型自己去提炼，然后存入memory
        resp = await self.model.ainvoke(messages=extract_messages, tools=[])
        return [line.strip("- ") for line in resp.content.split("\n") if line.strip()]
