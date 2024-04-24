from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest

from scoutos.blocks.slack import GetChannels

FAKE_SLACK_TOKEN = "xobx-***"  # noqa: S105


def create_block():
    return GetChannels(
        {
            "key": "slack_get_channels",
            "token": FAKE_SLACK_TOKEN,
        }
    )


def get_fixture_path(filename: str) -> Path:
    """Return the local path for fixtures relative to this text file."""
    current_dir = Path(__file__).parent
    fixture_dir = Path.joinpath(current_dir, "fixtures")

    return Path.joinpath(fixture_dir, filename)


def get_fixture_contents(fixture_name: str) -> dict:
    """Return the contents of the given fixture."""
    fixture_path = get_fixture_path(fixture_name)

    with fixture_path.open("rb") as f:
        return json.load(f)


def mock_response(
    *,
    status: int = 200,
    json: dict | None = None,
    text: str | None = None,
):
    json = json or get_fixture_contents("get_channels_payload.json")
    if text:
        response = httpx.Response(status, text=text)
    else:
        response = httpx.Response(status, json=json)

    response._request = httpx.Request("GET", "https://slack.com/api/conversations.list")  # noqa: SLF001

    return response


@pytest.mark.asyncio()
async def test_it_makes_expected_request_when_run():
    stubbed_response = mock_response()
    block = create_block()

    with patch(
        "scoutos.blocks.slack.get_channels.httpx.AsyncClient.get",
        return_value=stubbed_response,
    ) as mock_request:
        result = await block.run({})

        mock_request.assert_called_once_with(
            "https://slack.com/api/conversations.list",
            headers={"Authorization": f"Bearer {FAKE_SLACK_TOKEN}"},
            params={"limit": 1000},
        )

        assert isinstance(result, list)
        assert len(result) > 0
