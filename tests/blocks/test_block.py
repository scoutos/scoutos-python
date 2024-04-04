import pytest

from scoutos.blocks import Block, BlockInitializationError


@pytest.mark.asyncio()
async def test_it_raises_if_not_initialized():
    class ImproperlyInitializedBlock(Block):
        def __init__(self, *, key: str):
            self._key = key

        async def run(self, run_input: dict) -> dict:
            return run_input

    block = ImproperlyInitializedBlock(key="the_key")

    with pytest.raises(BlockInitializationError):
        await block.outter_run({})


@pytest.mark.asyncio()
async def test_it_runs():
    class SomeBlockSubclass(Block):
        def __init__(self, *, key: str):
            super().__init__(key=key)

        async def run(self, run_input: dict) -> dict:
            return run_input

    block = SomeBlockSubclass(key="some_block_subclass")

    run_input = {"foo": "baz"}
    result = await block.outter_run(run_input)

    assert result.ok is True
    assert result.output == run_input
