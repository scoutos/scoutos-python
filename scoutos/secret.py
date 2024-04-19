from __future__ import annotations

import json
from typing import Literal

import httpx

from scoutos.utils import DefaultValue

SCOUTOS_SECRETS_ENDPOINT = "https://api.scoutos.com/v1/secrets"

Env = Literal["production", "preview", "development"]


class Secret:
    def __init__(
        self, key: str, *, default_value: str | None = None, env: Env = "production"
    ):
        self._env = env
        self._key = key
        self._default_value = DefaultValue(
            is_set=default_value is not None,
            value=default_value,
        )

    @property
    def env(self) -> str:
        return self._env

    @property
    def key(self) -> str:
        return self._key

    async def resolve(self) -> str:
        url = f"{SCOUTOS_SECRETS_ENDPOINT}/{self._key}"
        headers = {
            "Accepts": "application/json",
            "Authorization": "Bearer <WE-NEED-SECRET-KEY-HERE>",
        }

        async with httpx.AsyncClient() as httpx_client:
            response = await httpx_client.get(url, headers=headers)

        try:
            value = response.json()["value"]
            return str(value)
        except (json.decoder.JSONDecodeError, KeyError) as orig_exception:
            raise SecretNotFoundError(self) from orig_exception


class SecretNotFoundError(Exception):
    def __init__(self, secret: Secret):
        message = f"Secret not found (key: {secret.key}, env: {secret.env})"
        super().__init__(message)
