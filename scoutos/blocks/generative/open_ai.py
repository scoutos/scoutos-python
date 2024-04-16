from typing import Unpack

from openai import OpenAI as OGOpenAI

from scoutos.blocks import BlockCommonArgs

from .base import Generative
from .types import GenerativeOutput


class OpenAI(Generative):
    """Generative AI using OpenAI models."""

    BLOCK_TYPE = "generative_openai"

    def __init__(self, *, api_key: str, model: str, **kwargs: Unpack[BlockCommonArgs]):
        super().__init__(**kwargs)
        self._api_key = api_key
        self._model = model

    async def run(self, run_input: dict) -> GenerativeOutput:
        client = OGOpenAI(api_key=self._api_key)
        messages = run_input["messages"]
        response = client.chat.completions.create(
            model=self._model,
            messages=messages,
        )

        return {
            "id": response.id,
            "model": response.model,
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }
            if response.usage
            else None,
            "choices": [
                {
                    "index": choice.index,
                    "finish_reason": choice.finish_reason,
                    "message": {
                        "role": choice.message.role,
                        "content": choice.message.content or "",
                    },
                }
                for choice in response.choices
            ],
        }
