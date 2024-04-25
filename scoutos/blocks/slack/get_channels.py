from __future__ import annotations

import httpx
from pydantic import ValidationError

from scoutos.blocks import BlockExecutionError

from .base import Slack, SlackConfig
from .types import Channel


class GetChannelsConfig(SlackConfig):
    pass


class GetChannels(Slack):
    TYPE = "scoutos:slack:get_channels"

    async def run(self, _run_input: dict) -> list[Channel]:
        headers = self._headers
        params = {"limit": 1000}  # Note: This is the maximum allowed
        url = f"{self._http_api_url}/conversations.list"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()

                data = response.json()

                if not data.get("ok"):
                    message = data.get("error", "An unknown exception occurred")
                    raise BlockExecutionError(message)

                channel_data = data.get("channels")
                if not channel_data or not isinstance(channel_data, list):
                    message = "no channels returned"
                    raise BlockExecutionError(message)

                return [Channel(**channel_datum) for channel_datum in channel_data]

            except ValidationError as validation_error:
                message = "output failed data validation"
                raise BlockExecutionError(message) from validation_error
            except httpx.HTTPStatusError as http_status_error:
                message = "http request failed"
                raise BlockExecutionError(message) from http_status_error
