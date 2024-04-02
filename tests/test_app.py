import pytest

from scoutos import App
from scoutos.blocks import Identity


def initialize_app():
    blocks = [
        Identity(key="block_1"),
        Identity(key="block_2"),
        Identity(key="block_3"),
    ]

    return App(blocks=blocks)


def test_instanitation():
    app = initialize_app()
    assert isinstance(app, App)


@pytest.mark.asyncio()
async def test_it_can_be_run():
    app = initialize_app()
    result = await app.run()
    assert result.ok
