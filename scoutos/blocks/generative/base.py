from abc import abstractmethod

from scoutos.blocks import Block

from .types import GenerativeInput, GenerativeOutput


class Generative(Block[GenerativeInput, GenerativeOutput]):
    """A base for blocks that use generative AI to produce output."""

    def __init__(self, *, key: str):
        super().__init__(key=key)

    @abstractmethod
    async def run(self, run_input: GenerativeInput) -> GenerativeOutput: ...
