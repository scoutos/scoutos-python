import pytest

from scoutos.blocks import Block
from scoutos.blocks.slack.base import Slack

FAKE_SLACK_TOKEN = "xoxb-***"  # noqa: S105


@pytest.fixture()
def block():
    class SomeSlackBlock(Slack[dict, dict]):
        TYPE = "scoutos:slack:some_block"

        async def run(self, run_input: dict) -> dict:
            return run_input

    return SomeSlackBlock(
        {
            "key": "some_slack_block",
            "token": FAKE_SLACK_TOKEN,
        }
    )


def test_inheritence(block):
    assert isinstance(block, Block)
    assert isinstance(block, Slack)


def test_it_defines_http_api_url_correctly(block):
    assert block._http_api_url == "https://slack.com/api"  # noqa: SLF001


def test_it_defines_headers_correctly(block):
    assert block._headers == {"Authorization": f"Bearer {FAKE_SLACK_TOKEN}"}  # noqa: SLF001
