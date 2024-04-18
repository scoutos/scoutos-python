import pytest
from httpx import HTTPError

from scoutos.blocks import Block, BlockExecutionError, Http


def test_initialization():
    obj = Http(key="test_http_block", url="https://some.url.com")

    assert isinstance(obj, Block)
    assert isinstance(obj, Http)


@pytest.mark.asyncio()
async def test_response_when_ok():
    block = Http(
        key="test_http_block", url="https://www.tnez.dev", response_type="text"
    )

    result = await block.run({})

    assert result


@pytest.mark.asyncio()
async def test_response_when_fails(monkeypatch):
    def mock_httpx_request() -> None:
        message = "This be the err"
        raise HTTPError(message)

    monkeypatch.setattr(
        "scoutos.blocks.http.httpx.AysncClient",
        mock_httpx_request,
    )
    block = Http(
        key="test_http_block_failing",
        url="https://www.tnez.dev",
    )

    with pytest.raises(BlockExecutionError):
        await block.run({})
