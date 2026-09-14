from contextlib import asynccontextmanager
import json
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from mini_agno.agent import Agent
from mini_agno.models.openai_model import OpenAIModel
from fastapi import FastAPI

from mini_agno.tools.decorator import my_tool

class RunRequest(BaseModel):
    message: str
    session_id: str = "default"
    user_id: str = "default"

class RunResponse(BaseModel):
    content: str

@my_tool
def query_temperature(bake_house:str):
    """根据烤房查询烤房的温度"""
    return "38.2"

@my_tool
def query_humidity(bake_house:str):
    """根据烤房查询烤房的湿度"""
    return "80.1"

agent = Agent(model=OpenAIModel(),tools=[query_temperature, query_humidity],instructions="你是一个 helpful的助手，根据用户输入的烤房名称，查询烤房的温度和湿度，并给出分析。")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App starting...")
    yield
    print("App closing...")
    await agent.model.aclose()

app = FastAPI(lifespan=lifespan)

@app.post("/chat")
def chat(request: RunRequest) -> RunResponse:
    return RunResponse(content=agent.run(request.message, request.session_id, request.user_id))

@app.post("/chat_stream")
async def chat_stream(request: RunRequest):
    async def sse():
        async for r in agent.arun_stream(request.message, request.session_id, request.user_id):
            if r.content:
                # f"data: ...\n\n" 的两个换行是 SSE 协议的帧终结符，少一个 curl/浏览器认为帧没结束
                yield f"data: {json.dumps({'content': r.content}, ensure_ascii=False)}\n\n"
    return StreamingResponse(sse(), media_type="text/event-stream")
