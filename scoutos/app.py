from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:  # pragma: no cover
    from scoutos.blocks import Block


@dataclass
class RunResult:
    """Result returned when App is run."""

    ok: bool


class App:
    """App is the entrypoint to ScoutOS Gen-AI Powered Applications."""

    def __init__(self, *, blocks: Sequence[Block]):
        self._blocks = blocks

    async def run(self) -> RunResult:
        """Run the application.

        This will invoke `run` on each of the individual blocks that make up the
        application, until the termination point is reached.
        """
        for block in self._blocks:
            await block.run({})

        return RunResult(ok=True)
