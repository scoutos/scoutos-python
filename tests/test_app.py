import pytest

from scoutos import App, AppExecutionError, Depends
from scoutos.blocks import Input, Output, Template


def test_instanitation():
    app = App(
        blocks=[
            Input(key="input"),
            Output(key="output"),
        ]
    )
    assert isinstance(app, App)


def test_get_output_raises_if_not_present():
    app = App(blocks=[])

    missing_block_id = "missing_block_id"
    with pytest.raises(AppExecutionError, match=missing_block_id):
        app.get_output(missing_block_id)


@pytest.mark.asyncio()
async def test_simple_sequential_run():
    app = App(
        blocks=[
            Input(key="input"),
            Template(
                key="template",
                depends=[
                    Depends.StrType("input.first_name"),
                    Depends.StrType("input.last_name"),
                ],
                template="Hello {{first_name}} {{last_name}}. Nice to meet you!",
            ),
            Output(key="output", depends=[Depends.StrType("template.result")]),
        ]
    )
    app_run_input = {"first_name": "Chili", "last_name": "Davis"}
    result = await app.run(app_run_input)

    assert result.ok

    block_ids_from_output = [
        output_entry.block_id for output_entry in result.block_output
    ]
    assert block_ids_from_output == ["input", "template", "output"]

    assert result.app_output == {"result": "Hello Chili Davis. Nice to meet you!"}


@pytest.mark.asyncio()
async def test_looping_run():
    """In this test, we demonstrate how it is possible to loop. We provide a
    target value and we expect that the looping_block is run `n` times."""
    looper_key = "looper"
    n = 5

    def stop_condition(data: dict) -> bool:
        return data["result"] >= data["n"]

    app = App(
        blocks=[
            Input(key="input"),
            Template(
                key=looper_key,
                depends=[
                    Depends.IntType("input.n"),
                    Depends.IntType(
                        f"{looper_key}.result",
                        default_value=0,
                    ),
                ],
                run_until=stop_condition,
                template="{{result + 1}}",
            ),
            Output(
                key="output",
                depends=[Depends.IntType(f"{looper_key}.result", key="count")],
            ),
        ]
    )

    app_run_input = {"n": n}

    result = await app.run(app_run_input)

    assert result.ok

    assert result.app_output["count"] == n
