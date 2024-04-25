from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest

from scoutos.blocks import BlockExecutionError
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


HTTPX_GET_PATCH_PATH = "scoutos.blocks.slack.get_channels.httpx.AsyncClient.get"


@pytest.mark.asyncio()
async def test_it_makes_expected_request_when_run():
    stubbed_response = mock_response()
    block = create_block()

    with patch(
        HTTPX_GET_PATCH_PATH,
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


@pytest.mark.asyncio()
async def test_when_slack_api_returns_with_error():
    block = create_block()
    stubbed_response = mock_response(json={"ok": False, "error": "some_error"})

    with patch(HTTPX_GET_PATCH_PATH, return_value=stubbed_response), pytest.raises(
        BlockExecutionError, match="some_error"
    ):
        await block.run({})


@pytest.mark.asyncio()
async def test_when_request_fails():
    block = create_block()
    stubbed_response = mock_response(status=500, text="Internal Server Error")

    with patch(HTTPX_GET_PATCH_PATH, return_value=stubbed_response), pytest.raises(
        BlockExecutionError, match="http request failed"
    ):
        await block.run({})


@pytest.mark.asyncio()
async def test_when_no_channel_data_is_returned():
    block = create_block()
    stubbed_response = mock_response(json={"ok": True})

    with patch(HTTPX_GET_PATCH_PATH, return_value=stubbed_response), pytest.raises(
        BlockExecutionError,
        match="no channels returned",
    ):
        await block.run({})


@pytest.mark.asyncio()
async def test_when_invalid_user_data_returned():
    block = create_block()
    stubbed_response = mock_response(
        json={"ok": True, "channels": [{"missing": "required_keys"}]}
    )

    with patch(HTTPX_GET_PATCH_PATH, return_value=stubbed_response), pytest.raises(
        BlockExecutionError,
        match="output failed data validation",
    ):
        await block.run({})
