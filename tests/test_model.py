import pytest

from mini_agno.models.message import Message


def test_abstract_model_cannot_be_instantiated():
    with pytest.raises(TypeError):
        from mini_agno.models.base import Model

        model = Model(id="test_model")


def test_mock_model():
    from mini_agno.models.mock import MockModel
    from mini_agno.models.message import ModelResponse

    resp1 = ModelResponse(content="mocked response 1")
    resp2 = ModelResponse(content="mocked response 2")
    response_list = [resp1, resp2]
    model = MockModel(id="test_model", response_list=response_list)
    msg = Message(role="user", content="Hello, world!")
    msg2 = Message(role="assistant", content="This is a test.")
    response = model.invoke(messages=[msg, msg2])
    print(response)
    assert response.content == response_list[0].content
