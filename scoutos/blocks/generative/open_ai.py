from typing import Required

from openai import OpenAI as OGOpenAI

from scoutos.blocks import BlockBaseConfig

from .base import Generative
from .types import GenerativeOutput


class OpenAIConfig(BlockBaseConfig):
    api_key: Required[str]
    model: Required[str]


class OpenAI(Generative):
    """Generative AI using OpenAI models."""

    TYPE = "generative_openai"

    def __init__(self, config: OpenAIConfig):
        super().__init__(config)
        self._api_key = config["api_key"]
        self._model = config["model"]

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
