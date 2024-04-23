from typing import Required

import pytest

from scoutos.blocks.base import (
    Block,
    BlockBaseConfig,
    BlockInitializationError,
    BlockOutput,
)
from scoutos.dependencies import Depends


class MinimalBlockStub(Block):
    TYPE = "test_minimal_block_stub"

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

    with pytest.raises(TypeError, match="Expected type to be provided"):
        Block.load(data)


def test_it_raises_when_invalid_block_type_is_provided():
    with pytest.raises(TypeError, match="TYPE"):

        class BlockMissingBlockType(Block):
            pass


def test_it_raises_when_unregisterd_block_type_provided():
    data = {
        "type": "unregistered_block_type",
    }

    with pytest.raises(ValueError, match="not registered"):
        Block.load(data)


def test_it_loads_from_valid_data():
    class SomeBlockConfig(BlockBaseConfig, total=False):
        foo: Required[str]
        baz: str

    class SomeBlock(Block):
        TYPE = "test_some_block"

        def __init__(self, config: SomeBlockConfig):
            super().__init__(config)
            self._foo = config["foo"]
            self._baz = config.get("baz", "default_value")

        async def run(self, run_input: dict) -> dict:
            return run_input

    data = {"type": SomeBlock.TYPE, "key": "some_block", "foo": "baz"}

    some_block_instance = Block.load(data)

    assert isinstance(some_block_instance, SomeBlock)
    assert isinstance(some_block_instance, Block)


def test_it_raises_when_missing_key():
    class AnotherBlock(Block):
        TYPE = "test_another_block"

        def __init__(self, config: BlockBaseConfig):
            super().__init__(config)

        async def run(self, run_input: dict) -> dict:
            return run_input

    data = {"type": AnotherBlock.TYPE}

    with pytest.raises(TypeError, match="key"):
        Block.load(data)


@pytest.mark.asyncio()
async def test_it_raises_if_not_initialized_with_super():
    class ImproperlyInitializedBlock(Block):
        TYPE = "test_improperly_initialized_block"

        def __init__(self, config: BlockBaseConfig):
            self._key = config["key"]

        async def run(self, run_input: dict) -> dict:
            return run_input

    block = ImproperlyInitializedBlock({"key": "some_key"})

    with pytest.raises(BlockInitializationError):
        await block.outter_run([])


@pytest.mark.asyncio()
async def test_it_runs():
    class SomeBlockSubclassConfig(BlockBaseConfig, total=False):
        suffix: Required[str]

    class SomeBlockSubclass(Block):
        TYPE = "test_some_block_subclass"

        def __init__(self, config: SomeBlockSubclassConfig):
            super().__init__(config)
            self._suffix = config["suffix"]

        async def run(self, run_input: dict) -> dict:
            return {"result": run_input["foo"] + self._suffix}

    block = SomeBlockSubclass(
        {
            "key": "some_block_subclass",
            "suffix": "--bazoo",
            "depends": [Depends.StrType({"path": "input.foo"})],
        }
    )
    current_output = [create_block_output("input", {"foo": "baz"})]
    result = await block.outter_run(current_output)

    assert result.ok is True
    assert result.output == {"result": "baz--bazoo"}


def test_input_schema():
    """If not provided, input schema should default to empty obj"""

    class SomeBlock(Block):
        TYPE = "test_some_block"

        async def run(self, _run_input: dict) -> dict:
            return {}

    block = SomeBlock({"key": "test:some_block"})

    assert block.input_schema == {}


def test_output_schema():
    """If not provided, output schema should default to empty obj"""

    class SomeBlock(Block):
        TYPE = "test_some_block"

        async def run(self, _run_input: dict) -> dict:
            return {}

    block = SomeBlock({"key": "test:some_block"})

    assert block.output_schema == {}
