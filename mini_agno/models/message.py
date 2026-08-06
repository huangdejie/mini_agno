from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


class ModelResponse(BaseModel):
    content: str


class RunResponse(BaseModel):
    content: str
    messages: list[Message]
