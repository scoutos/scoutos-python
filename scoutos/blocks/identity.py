from __future__ import annotations

from .base import Block, BlockBaseConfig


class Identity(Block):
    """The Identity Block outputs the same input it was given.

    This block may be useful for testing and debugging.
    """

    TYPE = "scoutos_identity"

    def __init__(self, config: BlockBaseConfig):
        super().__init__(config)

    async def run(self, run_input: dict) -> dict:
        return run_input
