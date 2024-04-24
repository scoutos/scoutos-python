from scoutos.blocks import Block
from scoutos.blocks.slack.base import Slack


def test_extending_from_base():
    class SomeSlackBlock(Slack[dict, dict]):
        TYPE = "scoutos:slack:some_block"

        async def run(self, run_input: dict) -> dict:
            return run_input

    block = SomeSlackBlock(
        {
            "key": "some_slack_block",
            "token": "FAKE_SLACK_TOKEN",
        }
    )

    assert isinstance(block, Block)
    assert isinstance(block, Slack)
    assert isinstance(block, SomeSlackBlock)
