import pytest

from scoutos.blocks import Block, Function


def test_loading():
    block = Function({"key": "function_block", "fn": lambda data: data})

    assert isinstance(block, Function)
    assert isinstance(block, Block)


@pytest.mark.asyncio()
async def test_with_simple_function():
    def sum_values(data: dict) -> dict:
        result = sum(data["values"])
        return {"result": result}

    block = Function(
        {
            "key": "function_block",
            "fn": sum_values,
        }
    )
    result = await block.run({"values": [1, 2, 3]})

    assert result == {"result": 6}
