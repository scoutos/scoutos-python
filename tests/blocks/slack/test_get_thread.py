from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest

from scoutos.blocks.base import BlockExecutionError
from scoutos.blocks.slack import GetThread

FAKE_TOKEN = "xoxb-***"  # noqa: S105
FAKE_CHANNEL_ID = "CXXX"
FAKE_TS = "1712163070.080049"

HTTPX_GET_PATCH_PATH = "scoutos.blocks.slack.get_messages.httpx.AsyncClient.get"


def create_block():
    return GetThread(
        {
            "key": "slack_get_thread",
            "token": FAKE_TOKEN,
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
        "GET", "https://slack.com/api/conversations.replies"
    )

    return response


@pytest.mark.asyncio()
async def test_happy_path(get_fixture_data):
    block = create_block()
    stubbed_response = create_stubbed_response(
        json=get_fixture_data("tests/blocks/slack/fixtures/get_thread_payload.json")
    )

    with patch(
        HTTPX_GET_PATCH_PATH, return_value=stubbed_response
    ) as mock_http_request:
        result = await block.run({"channel": FAKE_CHANNEL_ID, "ts": FAKE_TS})

        mock_http_request.assert_called_once_with(
            "https://slack.com/api/conversations.history",
            headers={"Authorization": f"Bearer {FAKE_TOKEN}"},
            json={
                "channel": FAKE_CHANNEL_ID,
                "ts": FAKE_TS,
                "cursor": None,
                "latest": None,
                "limit": None,
                "oldest": None,
            },
        )

        assert result is not None


#
#
# @pytest.mark.asyncio()
# async def test_when_slack_api_returns_error():
#     block = create_block()
#     stubbed_response = create_stubbed_response(
#         json={"ok": False, "error": "some_error"}
#     )
#
#     with patch(
#         HTTPX_GET_PATCH_PATH,
#         return_value=stubbed_response,
#     ), pytest.raises(BlockExecutionError, match="some_error"):
#         await block.run({})
#
#
# @pytest.mark.asyncio()
# async def test_when_slack_api_returns_invalid_data():
#     block = create_block()
#     stubbed_response = create_stubbed_response(json={"ok": True})
#
#     with patch(
#         HTTPX_GET_PATCH_PATH,
#         return_value=stubbed_response,
#     ), pytest.raises(BlockExecutionError, match="data validation"):
#         await block.run({})
#
#
# @pytest.mark.asyncio()
# async def test_when_reqeust_fails():
#     block = create_block()
#     stubbed_response = create_stubbed_response(status=500, text="Internal Server Error")
#
#     with patch(
#         HTTPX_GET_PATCH_PATH,
#         return_value=stubbed_response,
#     ), pytest.raises(BlockExecutionError, match="http request failed"):
#         await block.run({})
