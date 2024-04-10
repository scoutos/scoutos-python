from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar
from uuid import uuid4

from scoutos.utils import get_current_timestamp

if TYPE_CHECKING:  # pragma: no cover
    from scoutos.blocks.base import Block, BlockOutput


InitialInput = TypeVar("InitialInput", bound=dict)


@dataclass
class RunResult:
    """Result returned when App is run."""

    app_output: dict
    app_run_end_ts: str
    app_run_id: str
    app_run_start_ts: str
    block_output: list[BlockOutput]
    ok: bool
    session_id: str


class App:
    """App is the entrypoint to ScoutOS Gen-AI Powered Applications."""

    def __init__(self, *, blocks: list[Block]):
        self._blocks = {block.key: block for block in blocks}
        self._block_outputs: list[BlockOutput] = []
        self._initial_input: dict = {}

    @property
    def current_output(self) -> list[BlockOutput]:
        return self._block_outputs

    def get_block(self, block_id: str) -> Block:
        return self._blocks[block_id]

    def persist_output(self, output: BlockOutput) -> None:
        self._block_outputs.append(output)

    def get_output(self, block_id: str) -> BlockOutput:
        for block in self.current_output[::-1]:
            if block.block_id == block_id:
                return block

        message = f"Output for `block_id`: {block_id} not found"
        raise AppExecutionError(message)

    async def run(
        self,
        app_run_input: dict | None = None,
        *,
        run_until: str = "output",
        session_id: str | None = None,
    ) -> RunResult:
        """Run the application."""

        app_run_id = str(uuid4())
        session_id = session_id or str(uuid4())
        app_run_start_ts = get_current_timestamp()

        await self._run_until(run_until, initial_input=app_run_input)

        app_run_end_ts = get_current_timestamp()

        return RunResult(
            app_output=self.get_output("output").output,
            app_run_end_ts=app_run_end_ts,
            app_run_id=app_run_id,
            app_run_start_ts=app_run_start_ts,
            block_output=self.current_output,
            ok=True,
            session_id=session_id,
        )

    async def _run_until(
        self,
        block_id: str,
        *,
        initial_input: dict | None = None,
    ) -> None:
        initial_input = initial_input or {}
        current_block = self.get_block(block_id)

        for dep in current_block.depends:
            if dep.is_resolved(self.current_output):
                continue

            await self._run_until(
                dep.block_id,
                initial_input=initial_input,
            )

        current_block_output = await current_block.outter_run(
            self.current_output,
            override_input=initial_input if current_block.key == "input" else None,
        )
        self.persist_output(current_block_output)

        while current_block.key != "input" and current_block.requires_rerun(
            self.current_output
        ):
            current_block_output = await current_block.outter_run(self.current_output)
            self.persist_output(current_block_output)


class AppExecutionError(Exception):
    pass
