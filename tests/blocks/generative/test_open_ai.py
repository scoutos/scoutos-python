from __future__ import annotations

import pickle
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

from scoutos.blocks import Block
from scoutos.blocks.generative import Generative, OpenAI

if TYPE_CHECKING:  # pragma: no cover
    from scoutos.blocks.generative.types import GenerativeInput, GenerativeOutput


def get_fixture_path(fixture_name: str) -> Path:
    """Return the local path for fixtures relative to this text file."""
    current_dir = Path(__file__).parent
    fixture_dir = Path.joinpath(current_dir, "fixtures")

    return Path.joinpath(fixture_dir, f"{fixture_name}.pkl")


def get_fixture_contents(fixture_name: str) -> Any:
    """Return the contents of the given fixture."""
    fixture_path = get_fixture_path(fixture_name)

    with fixture_path.open("rb") as f:
        return pickle.load(f)  # noqa: S301


def write_fixture(obj: Any, fixture_name: str):
    """This can be used to write out response data to a fixture.

    To use, uncomment any mocking that is done, hit the real service, and use
    this convenience function to write out the response. This will write out the
    contents to following path:

    `tests/blocks/generative/fixtures/{fixture_name}.json``
    """
    fixture_path = get_fixture_path(fixture_name)
    with fixture_path.open("wb") as f:
        pickle.dump(obj, f)

    print(f"Wrote obj to {fixture_path}")  # noqa: T201


def initialize_block(
    *,
    api_key: str = "sooper-secret-api-key-shush",
    key: str = "test-generative-block",
    model: str = "gpt-3.5-turbo",
):
    return OpenAI(
        api_key=api_key,
        key=key,
        model=model,
    )


def test_initialization():
    block = initialize_block()

    assert isinstance(block, Block)
    assert isinstance(block, Generative)
    assert isinstance(block, OpenAI)


@pytest.mark.asyncio()
async def test_run(mocker):
    mock_openai_class = mocker.patch("scoutos.blocks.generative.open_ai.OGOpenAI")

    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    mock_client.chat.completions.create.return_value = get_fixture_contents(
        "open_ai_completion_response"
    )

    run_input: GenerativeInput = {
        "messages": [
            {
                "role": "system",
                "content": "You are a stubborn assitant who only replies with a single 'hello' no matter what the user asks you.",  # noqa: E501
            },
            {
                "role": "user",
                "content": "What is the weather like in San Francisco next Friday?",
            },
        ]
    }

    expected_output: GenerativeOutput = {
        "id": "chatcmpl-9A1NXZruNFoJV4IEH9jIZobebHJxJ",
        "model": "gpt-3.5-turbo-0125",
        "usage": {
            "input_tokens": 45,
            "output_tokens": 2,
        },
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {
                    "content": "Hello.",
                    "role": "assistant",
                },
            }
        ],
    }

    block = initialize_block()
    result = await block.run(run_input)

    mock_client.chat.completions.create.assert_called_once_with(
        model="gpt-3.5-turbo",
        messages=run_input["messages"],
    )

    # # To re-record the fixture data for the OpenAI client:
    # # 1) Modify `open_ai.py` to return entire OpenAI completion response.
    # # 2) Add valid api key to `initialize_block(api_key="<a-valid-key>")` above
    # # 3) Uncomment the line below.
    # # 4) Run tests
    # # 5) Verify results and then back out all changes
    # write_fixture(result.output, "open_ai_completion_response")  # noqa: ERA001

    assert result == expected_output
