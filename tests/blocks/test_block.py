from typing import Unpack

import pytest

from scoutos.blocks.base import (
    Block,
    BlockCommonArgs,
    BlockInitializationError,
    BlockOutput,
)
from scoutos.dependencies import Depends


class MinimalBlockStub(Block):
    async def run(self, run_input: dict) -> dict:
        return run_input


def create_block_output(block_id: str, output: dict) -> BlockOutput:
    return BlockOutput(
        block_id=block_id,
        block_run_id="BLOCK-RUN-ID-1234",
        block_run_end_ts="1970-01-01T00:00:000Z",
        block_run_start_ts="1970-01-01T00:00:000Z",
        ok=True,
        output=output,
    )


@pytest.mark.asyncio()
async def test_it_raises_if_not_initialized():
    class ImproperlyInitializedBlock(Block):
        def __init__(self, *, key: str):
            self._key = key

        async def run(self, run_input: dict) -> dict:
            return run_input

    block = ImproperlyInitializedBlock(key="the_key")

    with pytest.raises(BlockInitializationError):
        await block.outter_run([])


@pytest.mark.asyncio()
async def test_it_runs():
    class SomeBlockSubclass(Block):
        def __init__(self, *, suffix: str, **kwargs: Unpack[BlockCommonArgs]):
            super().__init__(**kwargs)
            self._suffix = suffix

        async def run(self, run_input: dict) -> dict:
            return {"result": run_input["foo"] + self._suffix}

    block = SomeBlockSubclass(
        key="some_block_subclass",
        suffix="--bazoo",
        depends=[Depends.StrType("input.foo")],
    )
    current_output = [create_block_output("input", {"foo": "baz"})]
    result = await block.outter_run(current_output)

    assert result.ok is True
    assert result.output == {"result": "baz--bazoo"}
