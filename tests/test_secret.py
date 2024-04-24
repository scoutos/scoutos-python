import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from scoutos import Secret, SecretNotFoundError


@pytest.mark.asyncio()
async def test_it_gets_a_secret_from_local_env_when_present():
    key = "SOME_KEY"
    expected_value = "EXPECTED_VALUE"

    secret = Secret(key="SOME_KEY")

    with patch.dict(os.environ, {key: expected_value}), patch.object(
        Secret, "_resolve_from_scout_cloud", MagicMock()
    ) as mock_resolve_from_scout_cloud:
        value = await secret.resolve()

        mock_resolve_from_scout_cloud.assert_not_called()
        assert value == "EXPECTED_VALUE"


@pytest.mark.asyncio()
async def test_it_raises_when_resolving_from_scout_cloud_without_secret_key():
    secret = Secret(key="SOME_KEY_THAT_DOES_NOT_EXIST_IN_LOCAL_ENV")

    with pytest.raises(ValueError, match="`scoutos_secret_key` is required"):
        await secret.resolve()


@pytest.mark.asyncio()
async def test_it_resolves_value_from_scout_cloud():
    key = "SECRET_PRESENT_IN_SCOUT_CLOUD"
    expected_value = "EXPECTED_VALUE"
    secret = Secret(key=key, scoutos_secret_key="FAKE_SECRET_KEY")  # noqa: S106

    with patch.object(
        Secret, "_resolve_from_local_env", MagicMock(return_value=None)
    ) as mock_resolve_from_local_env, patch(
        "scoutos.secret.httpx.AsyncClient.get",
        return_value=httpx.Response(200, json={"value": expected_value}),
    ):
        result = await secret.resolve()

        mock_resolve_from_local_env.assert_called_once()
        assert result == expected_value


@pytest.mark.asyncio()
async def test_when_request_to_scout_cloud_fails():
    key = "SOME_KEY"
    secret = Secret(key=key, scoutos_secret_key="FAKE_SECRET_KEY")  # noqa: S106

    with patch(
        "scoutos.secret.httpx.AsyncClient.get",
        return_value=httpx.Response(500, text="Internal Server Error"),
    ), pytest.raises(SecretNotFoundError, match=key):
        await secret.resolve()


@pytest.mark.asyncio()
async def test_when_secret_is_not_found_anywhere():
    key = "SOME_KEY_THAT_DOES_NOT_EXIST_IN_LOCAL_ENV"
    secret = Secret(key=key, scoutos_secret_key="FAKE_SECRET_KEY")  # noqa: S106

    with patch.object(
        Secret, "_resolve_from_scout_cloud", AsyncMock(return_value=None)
    ), pytest.raises(SecretNotFoundError, match=key):
        await secret.resolve()
