from __future__ import annotations

from typing import Callable

from .base import Block, BlockBaseConfig


class FunctionConfig(BlockBaseConfig):
    fn: Callable[[dict], dict]
    """The function that will be called when the block is run"""


class Function(Block):
    TYPE = "scoutos_function"

    def __init__(self, config: FunctionConfig):
        super().__init__(config)
        self._config: FunctionConfig = config

    async def run(self, run_input: dict) -> dict:
        return self._config["fn"](run_input)
