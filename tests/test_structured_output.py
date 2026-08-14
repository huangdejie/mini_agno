from pydantic import BaseModel

from mini_agno.models.mock import MockModel
from mini_agno.models.message import ModelResponse
from mini_agno.agent import Agent


class Weather(BaseModel):
    city: str
    temperature: int


def test_structured_output():
    weather = Weather(city="Beijing", temperature=25)

    mock_model = MockModel(
        id="test_model",
        response_list=[
            ModelResponse(
                content=weather.model_dump_json(),
                tool_calls=None,
            )
        ],
    )
    agent = Agent(model=mock_model, tools=[], output_schema=Weather)
    res = agent.run("beijing天气怎么样")
    assert isinstance(res, Weather)
    assert res.city == "Beijing"
    assert res.temperature == 25
