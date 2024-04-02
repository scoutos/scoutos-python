from typing import TypeVar

from .base import Block

T = TypeVar("T", bound=dict)


class Identity(Block):
    """The Identity Block outputs the same input it was given.

    This block may be useful for testing and debugging.
    """

    def __init__(self, *, key: str):
        super().__init__(key=key)

    async def run(self, run_input: T) -> T:
        return run_input
