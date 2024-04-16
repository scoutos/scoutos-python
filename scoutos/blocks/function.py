from __future__ import annotations

from typing import Callable, Unpack

from .base import Block, BlockCommonArgs

Fn = Callable[[dict], dict]


class Function(Block):
    """The Identity Block outputs the same input it was given.

    This block may be useful for testing and debugging.
    """

    BLOCK_TYPE = "scoutos_function"

    def __init__(self, fn: Fn, **kwargs: Unpack[BlockCommonArgs]):
        super().__init__(**kwargs)
        self._fn = fn

    async def run(self, run_input: dict) -> dict:
        return self._fn(run_input)
