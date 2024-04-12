# noqa: INP001
import asyncio
import sys

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

from scoutos import App, Depends
from scoutos.blocks import Function, Input, Output
from scoutos.blocks.generative import OpenAI
from scoutos.env import get_env

load_dotenv()
OPENAI_API_KEY = get_env("OPENAI_API_KEY")


SYSTEM_PROMPT = """
You are a surly assistant named Larry Fitzpatrick. Your job is to answer the
user's question as effectively as possible, but be sure to let them know that
you are not happy about it.
"""


class AppInput(BaseModel):
    prompt: str
    """The prompt to be supplied to the generative block."""


blocks = [
    Input(key="input"),
    Function(
        key="prepare_messages",
        depends=[Depends.StrType("input.prompt")],
        fn=lambda data: {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": data["prompt"]},
            ]
        },
    ),
    OpenAI(
        key="llm",
        depends=[Depends.AnyType("prepare_messages.messages")],
        api_key=OPENAI_API_KEY,
        model="gpt-4-turbo",
    ),
    Function(
        key="parse_llm_response",
        depends=[Depends.AnyType("llm.choices")],
        fn=lambda data: {
            "completion": data["choices"][0]["message"]["content"],
        },
    ),
    Output(key="output", depends=[Depends.StrType("parse_llm_response.completion")]),
]

app = App(blocks=blocks)


async def main(app_input: AppInput) -> None:
    """
    This is a simple example illustrating how to use the ScoutOS SDK to run a
    simple application.

    Parameters:
    - app_input (AppInput): The input data required for the application to run.

    Returns:
    - None: This function prints the result of the application run to the console.
    """
    result = await app.run(app_input.model_dump())
    print(result)


if __name__ == "__main__":
    try:
        app_input = AppInput.model_validate(
            {
                "prompt": sys.argv[1],
            }
        )
        asyncio.run(main(app_input))

    except ValidationError as exception:
        print(exception)
        print(main.__doc__)
