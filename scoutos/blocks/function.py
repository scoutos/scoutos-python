from __future__ import annotations

from typing import Callable, Required

from .base import Block, BlockBaseConfig


class FunctionConfig(BlockBaseConfig, total=False):
    fn: Required[Callable[[dict], dict]]
    """The function that will be called when the block is run"""


class Function(Block):
    TYPE = "scoutos_function"

    def __init__(self, config: FunctionConfig):
        super().__init__(config)
        self._fn = config["fn"]

    async def run(self, run_input: dict) -> dict:
        return self._fn(run_input)
