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
    BLOCK_TYPE = "test_minimal_block_stub"

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


def test_it_raises_when_block_type_is_not_provided():
    data = {}

    with pytest.raises(ValueError, match="Expected block_type to be provided"):
        Block.load(data)


def test_it_raises_when_invalid_block_type_is_provided():
    with pytest.raises(ValueError, match="BLOCK_TYPE"):

        class BlockMissingBlockType(Block):
            pass


def test_it_raises_when_unregisterd_block_type_provided():
    data = {
        "block_type": "unregistered_block_type",
    }

    with pytest.raises(ValueError, match="not registered"):
        Block.load(data)


def test_it_loads_from_valid_data():
    class SomeBlock(Block):
        BLOCK_TYPE = "test_some_block"

        def __init__(self, foo: str, **kwargs: Unpack[BlockCommonArgs]):
            super().__init__(**kwargs)
            self._foo = foo

        async def run(self, run_input: dict) -> dict:
            return run_input

    data = {"block_type": SomeBlock.BLOCK_TYPE, "key": "some_block", "foo": "baz"}

    some_block_instance = Block.load(data)

    assert isinstance(some_block_instance, SomeBlock)
    assert isinstance(some_block_instance, Block)


def test_it_raises_when_missing_key():
    class AnotherBlock(Block):
        BLOCK_TYPE = "test_another_block"

        def __init__(self, **kwargs: Unpack[BlockCommonArgs]):
            super().__init__(**kwargs)

        async def run(self, run_input: dict) -> dict:
            return run_input

    data = {"block_type": AnotherBlock.BLOCK_TYPE}

    with pytest.raises(KeyError, match="key"):
        Block.load(data)


@pytest.mark.asyncio()
async def test_it_raises_if_not_initialized_with_super():
    class ImproperlyInitializedBlock(Block):
        BLOCK_TYPE = "test_improperly_initialized_block"

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
        BLOCK_TYPE = "test_some_block_subclass"

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
