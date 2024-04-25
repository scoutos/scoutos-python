from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest

from scoutos.blocks import BlockExecutionError
from scoutos.blocks.slack import GetUserInfo

FAKE_SLACK_TOKEN = "xoxb-***"  # noqa: S105
FAKE_USER_ID = "UXXXXXXXXXX"
STUBBED_USER_INFO = {
    "ok": True,
    "user": {
        "deleted": False,
        "id": "UXXXXXXXXXX",
        "is_admin": True,
        "is_bot": False,
        "is_owner": True,
        "is_primary_owner": False,
        "name": "someuser",
        "real_name": "Some User",
        "team_id": "TXXXXXXXXXX",
    },
}


@pytest.fixture()
def block():
    return GetUserInfo(
        {
            "key": "slack_get_user_info",
            "token": FAKE_SLACK_TOKEN,
        }
    )


def mock_response(
    *,
    status: int = 200,
    json: dict | None = STUBBED_USER_INFO,
    text: str | None = None,
):
    if text:
        response = httpx.Response(status, text=text)
    else:
        response = httpx.Response(status, json=json)

    response._request = httpx.Request("GET", "https://slack.com/api/users.info")  # noqa: SLF001

    return response


@pytest.fixture()
def stubbed_response_valid():
    return {}


@pytest.mark.asyncio()
async def test_it_makes_expected_request_when_run(block):
    with patch(
        "scoutos.blocks.slack.get_user_info.httpx.AsyncClient.get",
        return_value=mock_response(),
    ) as request:
        await block.run({"user_id": FAKE_USER_ID})

        request.assert_called_once_with(
            "https://slack.com/api/users.info",
            headers={"Authorization": f"Bearer {FAKE_SLACK_TOKEN}"},
            params={"user": FAKE_USER_ID},
        )


@pytest.mark.asyncio()
async def test_it_strips_extra_keys_from_user_data(block):
    user_info_with_extra = STUBBED_USER_INFO.copy()
    user_info_with_extra["user"]["extra_key"] = "I am an extra key"
    with patch(
        "scoutos.blocks.slack.get_user_info.httpx.AsyncClient.get",
        return_value=mock_response(json=user_info_with_extra),
    ):
        result = await block.run({"user_id": FAKE_USER_ID})

        assert result.get("extra_key") is None


@pytest.mark.asyncio()
async def test_when_user_does_not_exist(block):
    with patch(
        "scoutos.blocks.slack.get_user_info.httpx.AsyncClient.get",
        return_value=mock_response(json={"ok": False, "error": "user_not_found"}),
    ), pytest.raises(BlockExecutionError, match="user_not_found"):
        await block.run({"user_id": FAKE_USER_ID})


@pytest.mark.asyncio()
async def test_when_request_fails(block):
    with patch(
        "scoutos.blocks.slack.get_user_info.httpx.AsyncClient.get",
        return_value=mock_response(status=500, text="Internal Server Error"),
    ), pytest.raises(BlockExecutionError, match="http request failed"):
        await block.run({"user_id": FAKE_USER_ID})


@pytest.mark.asyncio()
async def test_when_invalid_user_data_returned(block):
    stubbed_response = {"ok": True, "user": {}}
    with patch(
        "scoutos.blocks.slack.get_user_info.httpx.AsyncClient.get",
        return_value=mock_response(status=200, json=stubbed_response),
    ), pytest.raises(BlockExecutionError, match="output failed data validation"):
        await block.run({"user_id": FAKE_USER_ID})
