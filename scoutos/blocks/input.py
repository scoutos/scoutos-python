from __future__ import annotations

from typing import Unpack

from .base import Block, BlockCommonArgs

INPUT_BLOCK_ID = "input"


class Input(Block):
    """The Input block is a special block that starts all apps.

    It's responsiblity is to wrangle input and expose it to subsequent nodes.
    """

    def __init__(
        self,
        **kwargs: Unpack[BlockCommonArgs],
    ):
        kwargs["key"] = INPUT_BLOCK_ID
        super().__init__(**kwargs)

    async def run(self, run_input: dict) -> dict:
        return run_input
