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


def test_get_output_raises_if_not_present():
    app = App(blocks=[])

    missing_block_id = "missing_block_id"
    with pytest.raises(AppExecutionError, match=missing_block_id):
        app.get_output(missing_block_id)
