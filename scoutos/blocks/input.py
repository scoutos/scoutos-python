from __future__ import annotations

from .base import Block, BlockBaseConfig

INPUT_BLOCK_ID = "input"


class Input(Block):
    """The Input block is a special block that starts all apps.

    It's responsiblity is to wrangle input and expose it to subsequent nodes.
    """

    TYPE = "scoutos_input"

    def __init__(self, config: BlockBaseConfig):
        config["key"] = INPUT_BLOCK_ID
        super().__init__(config)

    async def run(self, run_input: dict) -> dict:
        return run_input
