from abc import abstractmethod

from scoutos.blocks import Block, BlockBaseConfig

from .types import GenerativeInput, GenerativeOutput


class Generative(Block[GenerativeInput, GenerativeOutput]):
    """A base for blocks that use generative AI to produce output."""

    _is_base_class = True

    def __init__(self, config: BlockBaseConfig):
        super().__init__(config)

    @abstractmethod
    async def run(self, run_input: dict) -> GenerativeOutput: ...
