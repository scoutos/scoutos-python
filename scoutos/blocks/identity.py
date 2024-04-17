from __future__ import annotations

from typing import Unpack

from .base import Block, BlockCommonArgs


class Identity(Block):
    """The Identity Block outputs the same input it was given.

    This block may be useful for testing and debugging.
    """

    TYPE = "scoutos_identity"

    def __init__(self, **kwargs: Unpack[BlockCommonArgs]):
        super().__init__(**kwargs)

    async def run(self, run_input: dict) -> dict:
        return run_input
