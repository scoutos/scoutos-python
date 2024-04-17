from abc import abstractmethod
from typing import Unpack

from scoutos.blocks import Block, BlockCommonArgs

from .types import GenerativeInput, GenerativeOutput


class Generative(Block[GenerativeInput, GenerativeOutput]):
    """A base for blocks that use generative AI to produce output."""

    _is_base_class = True

    def __init__(self, **kwargs: Unpack[BlockCommonArgs]):
        super().__init__(**kwargs)

    @abstractmethod
    async def run(self, run_input: dict) -> GenerativeOutput: ...
