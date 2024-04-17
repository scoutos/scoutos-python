from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar
from uuid import uuid4

from pydantic import BaseModel

from scoutos.blocks.base import Block
from scoutos.constants import THE_START_OF_TIME_AND_SPACE
from scoutos.utils import get_current_timestamp, read_data_from_file

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path

    from scoutos.blocks.base import BlockOutput


InitialInput = TypeVar("InitialInput", bound=dict)


class AppConfig(BaseModel):
    blocks: list[dict]


@dataclass
class RunResult:
    """Result returned when App is run."""

    app_output: dict
    app_run_end_ts: str
    app_run_id: str
    app_run_path: list[str]
    app_run_start_ts: str
    block_output: list[BlockOutput]
    ok: bool
    session_id: str

    def __str__(self) -> str:  # pragma: no cover
        return "\n".join(
            [
                f"App Id: {self.app_run_id}",
                f"Session Id: {self.session_id}",
                f"App Run Id: {self.app_run_id}",
                f"Run Started At: {self.app_run_start_ts}",
                f"Run Completed At: {self.app_run_end_ts}",
                f"Status: {self.ok}",
                f"Blocks Executed: {self.app_run_path}",
                "---",
                json.dumps(self.app_output, indent=2),
            ]
        )


class App:
    """App is the entrypoint to ScoutOS Gen-AI Powered Applications."""

    def __init__(self, blocks: list[Block]):
        self._blocks = {block.key: block for block in blocks}
        self._block_outputs: list[BlockOutput] = []
        self._initial_input: dict = {}

    @classmethod
    def load(cls, data: dict) -> App:
        config = AppConfig.model_validate(data)
        blocks = [Block.load(block_data) for block_data in config.blocks]
        return App(blocks)

    @classmethod
    def load_from_file(cls, path: Path) -> App:
        data = read_data_from_file(path)
        return cls.load(data)

    @property
    def blocks(self) -> dict[str, Block]:
        return self._blocks

    @property
    def current_output(self) -> list[BlockOutput]:
        return sorted(
            [output for block in self.blocks.values() for output in block.output],
            key=lambda block_output: block_output.block_run_end_ts,
        )

    @property
    def current_path(self) -> list[str]:
        """The path of blocks executed returned as a list of strings"""
        return [block_output.block_id for block_output in self.current_output]

    def get_block(self, block_id: str) -> Block:
        return self.blocks[block_id]

    def get_output(self, block_id: str) -> BlockOutput:
        try:
            return self.blocks[block_id].output[-1]
        except KeyError as orig_err:
            message = f"Output for `block_id`: {block_id} not found"
            raise AppExecutionError(message) from orig_err

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
            app_run_path=self.current_path,
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

        if current_block.has_exceeded_run_count:
            message = f"Exceeded Run Count for {current_block}"
            raise AppExecutionError(message)

        for dep in current_block.depends:
            if dep.is_resolved(
                self.current_output,
                since=current_block.last_run_completed_at or THE_START_OF_TIME_AND_SPACE
                if dep.requires_rerun
                else THE_START_OF_TIME_AND_SPACE,
            ):
                continue

            await self._run_until(
                dep.block_id,
                initial_input=initial_input,
            )

        await current_block.outter_run(
            self.current_output,
            override_input=initial_input if current_block.key == "input" else None,
        )

        if not current_block.has_met_termination_condition(self.current_output):
            await self._run_until(current_block.key)


class AppExecutionError(Exception):
    pass
