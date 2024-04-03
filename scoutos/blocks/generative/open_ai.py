from openai import OpenAI as OGOpenAI

from .base import Generative
from .types import GenerativeInput, GenerativeOutput


class OpenAI(Generative):
    """Generative AI using OpenAI models."""

    def __init__(self, *, key: str, api_key: str, model: str):
        super().__init__(key=key)
        self._api_key = api_key
        self._model = model

    async def run(self, run_input: GenerativeInput) -> GenerativeOutput:
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
