from unittest.mock import patch

import httpx
import pytest

from scoutos import Secret, SecretNotFoundError


@pytest.mark.asyncio()
@patch(
    "scoutos.secret.httpx.AsyncClient.get",
    return_value=httpx.Response(200, json={"value": "EXPECTED_VALUE"}),
)
async def test_it_gets_a_secret(mocker):  # noqa: ARG001
    secret = Secret(key="SOME_KEY")
    value = await secret.resolve()

    assert value == "EXPECTED_VALUE"


@pytest.mark.asyncio()
@patch(
    "scoutos.secret.httpx.AsyncClient.get",
    return_value=httpx.Response(200, json={"detail": "Some message about an error"}),
)
async def test_when_value_not_returned(mocker):  # noqa: ARG001
    secret = Secret(key="SOME_KEY")

    with pytest.raises(SecretNotFoundError, match="SOME_KEY"):
        await secret.resolve()


@pytest.mark.asyncio()
@patch(
    "scoutos.secret.httpx.AsyncClient.get",
    return_value=httpx.Response(500, text="Internal Server Error"),
)
async def test_when_request_fails(mocker):  # noqa: ARG001
    secret = Secret(key="SOME_KEY")

    with pytest.raises(SecretNotFoundError, match="SOME_KEY"):
        await secret.resolve()
