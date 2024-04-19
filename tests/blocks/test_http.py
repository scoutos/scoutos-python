from unittest.mock import patch

import httpx
import pytest

from scoutos.blocks import Block
from scoutos.blocks.http import Http


def test_initialization():
    obj = Http(key="test_http_block", url="https://some.url.com")

    assert isinstance(obj, Block)
    assert isinstance(obj, Http)


@pytest.mark.asyncio()
@patch(
    "scoutos.blocks.http.httpx.AsyncClient.request",
    return_value=httpx.Response(200, json={"foo": "baz"}),
)
async def test_json_response(mocker):  # noqa: ARG001
    block = Http(
        key="test_http_block", url="https://www.example.com", response_type="json"
    )

    result = await block.run({})

    assert result == {"result": {"foo": "baz"}}


@pytest.mark.asyncio()
@patch(
    "scoutos.blocks.http.httpx.AsyncClient.request",
    return_value=httpx.Response(200, text="This is the expected text"),
)
async def test_text_response(mocker):  # noqa: ARG001
    block = Http(
        key="test_http_block", url="https://www.example.com", response_type="text"
    )

    result = await block.run({})

    assert result == {"result": "This is the expected text"}
