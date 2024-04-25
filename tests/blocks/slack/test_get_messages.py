from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest

from scoutos.blocks.base import BlockExecutionError
from scoutos.blocks.slack import GetMessages

FAKE_TOKEN = "xoxb-***"  # noqa: S105
FAKE_CHANNEL_ID = "CXXX"

HTTPX_POST_PATCH_PATH = "scoutos.blocks.slack.get_messages.httpx.AsyncClient.post"


def create_block():
    return GetMessages(
        {
            "key": "slack_get_messages",
            "token": FAKE_TOKEN,
            "channel_id": FAKE_CHANNEL_ID,
        }
    )


def create_stubbed_response(
    *,
    status: int = 200,
    json: dict | None = None,
    text: str | None = None,
):
    if text:
        response = httpx.Response(status, text=text)
    else:
        response = httpx.Response(status, json=json)

    response._request = httpx.Request(  # noqa: SLF001
        "POST", "https://slack.com/api/conversations.history"
    )

    return response


@pytest.mark.asyncio()
async def test_happy_path(get_fixture_data):
    block = create_block()
    stubbed_response = create_stubbed_response(
        json=get_fixture_data("tests/blocks/slack/fixtures/get_messages_payload.json")
    )

    with patch(
        HTTPX_POST_PATCH_PATH, return_value=stubbed_response
    ) as mock_http_request:
        limit = 3
        result = await block.run({"limit": limit})

        mock_http_request.assert_called_once_with(
            "https://slack.com/api/conversations.history",
            headers={"Authorization": f"Bearer {FAKE_TOKEN}"},
            json={
                "channel": FAKE_CHANNEL_ID,
                "cursor": None,
                "latest": None,
                "limit": limit,
                "oldest": None,
            },
        )

        assert result is not None


@pytest.mark.asyncio()
async def test_when_slack_api_returns_error():
    block = create_block()
    stubbed_response = create_stubbed_response(
        json={"ok": False, "error": "some_error"}
    )

    with patch(
        HTTPX_POST_PATCH_PATH,
        return_value=stubbed_response,
    ), pytest.raises(BlockExecutionError, match="some_error"):
        await block.run({})


@pytest.mark.asyncio()
async def test_when_slack_api_returns_invalid_data():
    block = create_block()
    stubbed_response = create_stubbed_response(json={"ok": True})

    with patch(
        HTTPX_POST_PATCH_PATH,
        return_value=stubbed_response,
    ), pytest.raises(BlockExecutionError, match="data validation"):
        await block.run({})


@pytest.mark.asyncio()
async def test_when_reqeust_fails():
    block = create_block()
    stubbed_response = create_stubbed_response(status=500, text="Internal Server Error")

    with patch(
        HTTPX_POST_PATCH_PATH,
        return_value=stubbed_response,
    ), pytest.raises(BlockExecutionError, match="http request failed"):
        await block.run({})
