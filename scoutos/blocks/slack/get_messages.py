from __future__ import annotations

from typing import Literal

import httpx
from pydantic import BaseModel, ConfigDict, ValidationError

from scoutos.blocks import BlockExecutionError

from .base import Slack
from .types import Message, ResponseMetadata  # noqa: TCH001


class GetMessagesInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    channel: str
    """The ID of the channel from which to pull messages."""

    # cursor: str | None = None
    """Paginate through collections of data by setting the cursor parameter to
    a next_cursor attribute returned by a previous request's
    response_metadata. Default value fetches the first "page" of the
    collection. See pagination for more detail."""

    # latest: str | None = None
    """Only messages before this Unix timestamp will be included in results.
    Default is the current time."""

    # limit: int = 100
    """The maximum number of items to return. Fewer than the requested number of
    items may be returned, even if the end of the conversation history
    hasn't been reached. Maximum of 999."""

    # oldest: str = "0"
    """Only messages after this Unix timestamp will be included in results.
    Default is '0'.
    """


class GetMessagesOutput(BaseModel):
    ok: Literal[True]
    messages: list[Message]
    has_more: bool
    pin_count: int
    response_metadata: ResponseMetadata | None = None


class GetMessages(Slack):
    TYPE = "scoutos:slack:get_messages"

    async def run(self, run_input: dict) -> GetMessagesOutput:
        validated_input = GetMessagesInput.model_validate(run_input)

        headers = self._headers
        data = validated_input.model_dump()
        print("Data::")
        print(data)
        url = f"{self._http_api_url}/conversations.history"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()

                data = response.json()

                if not data.get("ok"):
                    message = data.get("error", "an unknown exception occurred")
                    print("Input::")
                    print(validated_input)
                    print("Response Data::")
                    print(data)
                    raise BlockExecutionError(message)

                return GetMessagesOutput.model_validate(data)

            except ValidationError as validation_error:
                message = "output failed data validation"
                raise BlockExecutionError(message) from validation_error

            except httpx.HTTPStatusError as http_status_error:
                message = "http request failed"
                raise BlockExecutionError(message) from http_status_error
