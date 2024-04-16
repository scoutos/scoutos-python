import pytest

from scoutos import App, AppExecutionError, Depends
from scoutos.blocks import Block, Identity, Input, Output, Template


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


def test_it_loads_from_valid_data():
    data = {
        "blocks": [
            {
                "block_type": Block.REGISTERED_BLOCKS["scoutos_input"].BLOCK_TYPE,
                "key": "test_input",
            },
            {
                "block_type": Block.REGISTERED_BLOCKS["scoutos_output"].BLOCK_TYPE,
                "key": "test_output",
            },
        ]
    }
    app = App.load(data)

    assert isinstance(app, App)


@pytest.mark.asyncio()
async def test_raises_if_block_has_exceeded_run_count():
    class WillExceedRuncount(Block):
        BLOCK_TYPE = "test_will_exceed_runcount"

        @property
        def has_exceeded_run_count(self) -> bool:
            return True

        async def run(self, run_input: dict) -> dict:
            return run_input

    app = App(
        blocks=[
            Input(key="input"),
            WillExceedRuncount(
                key="has_exceeded", depends=[Depends.StrType("input.foo")]
            ),
            Output(key="output", depends=[Depends.StrType("has_exceeded.foo")]),
        ]
    )

    with pytest.raises(AppExecutionError, match="Exceeded Run Count"):
        await app.run({"foo": "baz"})


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
    assert result.app_run_path == ["input", "template", "output"]
    assert result.app_output == {"result": "Hello Chili Davis. Nice to meet you!"}


@pytest.mark.asyncio()
async def test_looping_with_single_block():
    """In this test, we demonstrate how it is possible to loop. We provide a
    target value and we expect that the looping_block is run `n` times."""
    looper_key = "looper"

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

    app_run_input = {"n": 5}

    result = await app.run(app_run_input)

    assert result.ok
    assert result.app_run_path == [
        "input",
        "looper",
        "looper",
        "looper",
        "looper",
        "looper",
        "output",
    ]
    assert result.app_output["count"] == app_run_input["n"]


@pytest.mark.parametrize(
    ("n", "expected_path"),
    [
        (1, ["input", "increment", "coerce", "output"]),
        (2, ["input", "increment", "coerce", "increment", "coerce", "output"]),
    ],
)
@pytest.mark.asyncio()
async def test_looping_with_multiple_blocks(n, expected_path):
    """In this test, we demonstrate how it is possible to loop through a
    sequence of blocks, repeating the sequence until a condition is met."""

    blocks = [
        Input(key="input"),
        Template(
            key="increment",
            depends=[Depends.IntType("coerce.counter", default_value=0)],
            template="{{counter + 1}}",
        ),
        Identity(
            key="coerce",
            depends=[
                Depends.IntType("input.n"),
                Depends.IntType("increment.result", key="counter", requires_rerun=True),
            ],
            run_until=lambda data: data["counter"] >= data["n"],
        ),
        Output(
            key="output",
            depends=[
                Depends.IntType("input.n"),
                Depends.IntType("coerce.counter"),
            ],
        ),
    ]

    app = App(blocks=blocks)
    result = await app.run({"n": n})

    assert result.ok
    assert result.app_output == {"counter": n, "n": n}
    assert result.app_run_path == expected_path
