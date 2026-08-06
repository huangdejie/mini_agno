import pytest

from mini_agno.models.message import Message


def test_abstract_model_cannot_be_instantiated():
    with pytest.raises(TypeError):
        from mini_agno.models.base import Model

        model = Model(id="test_model")


def test_mock_model():
    from mini_agno.models.mock import MockModel

    model = MockModel(id="test_model", response="mocked response")
    msg = Message(role="user", content="Hello, world!")
    msg2 = Message(role="assistant", content="This is a test.")
    response = model.invoke([msg, msg2])
    assert response.content == "mocked response"
