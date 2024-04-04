from __future__ import annotations

from typing import TYPE_CHECKING, Unpack

from .base import Block

if TYPE_CHECKING:  # pragma: no cover
    from .base import BlockCommonArgs

OUTPUT_BLOCK_ID = "output"


class Output(Block):
    """The Output block is a special block that serves as the termination point
    for all apps.

    It is responsible for mapping previous block results to "ultimate" output
    for the application.
    """

    def __init__(self, **kwargs: Unpack[BlockCommonArgs]):
        kwargs["key"] = OUTPUT_BLOCK_ID
        super().__init__(**kwargs)

    async def run(self, run_input: dict) -> dict:
        return run_input
