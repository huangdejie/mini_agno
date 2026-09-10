from pydantic import BaseModel

from mini_agno.agent import Agent
from mini_agno.models.openai_model import OpenAIModel
from fastapi import FastAPI

class RunRequest(BaseModel):
    message: str
    session_id: str = "default"
    user_id: str = "default"

class RunResponse(BaseModel):
    content: str

agent = Agent(model=OpenAIModel(),tools=[])

app = FastAPI()

@app.post("/chat")
def chat(request: RunRequest) -> RunResponse:
    return RunResponse(content=agent.run(request.message, request.session_id, request.user_id))
