from mini_agno.models.message import RunResponse
from mini_agno.models.message import Message


def test_message():
    message = Message(role="user", content="Hello, world!")
    assert message.role == "user"
    assert message.content == "Hello, world!"
    msg = message.model_dump()
    Message.model_validate(msg)
    assert message == Message.model_validate(msg)


def test_run_response():
    run_response = RunResponse(content="Hello, world!", messages=[])
    assert run_response.content == "Hello, world!"
    assert run_response.messages == []
    msg_01 = Message(role="user", content="Hello, world!")
    msg_02 = Message(role="assistant", content="Hello, world!")
    run_response.messages.append(msg_01)
    run_response.messages.append(msg_02)
    assert run_response.messages == [msg_01, msg_02]
    msg = run_response.model_dump()
    RunResponse.model_validate(msg)
    assert run_response == RunResponse.model_validate(msg)
