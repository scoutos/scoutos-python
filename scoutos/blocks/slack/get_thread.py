from __future__ import annotations

from typing import Literal

import httpx
from pydantic import BaseModel, ConfigDict, ValidationError

from scoutos.blocks import BlockExecutionError

from .base import Slack
# from .types import Message, ResponseMetadata  # noqa: TCH001


class GetThreadInput(BaseModel):
    channel: str
    """Channel ID to which the thread belongs."""

    ts: str
    """Unique identifier of either a thread's parent message or a message in
    the thread. ts must be the timestamp of an existing message with 0 or
    more replies. If there are no replies then just the single message
    referenced by ts will return - it is just an ordinary, unthreaded
    message."""

    cursor: str | None = None
    """Paginate through collections of data by setting the cursor parameter to
    a next_cursor attribute returned by a previous request's
    response_metadata. Default value fetches the first "page" of the
    collection. See pagination for more detail."""

    latest: str | None = None
    """Only messages before this Unix timestamp will be included in results.
    Default is the current time."""

    limit: int | None = 100
    """The maximum number of items to return. Fewer than the requested number of
    items may be returned, even if the end of the conversation history
    hasn't been reached. Maximum of 999."""

    oldest: str | None = None
    """Only messages after this Unix timestamp will be included in results.
    Default is '0'.
    """


class GetThreadOutput(BaseModel):
    model_config = ConfigDict(extra="allow")
    # ok: Literal[True]
    # messages: list[Message]
    # has_more: bool
    # response_metadata: ResponseMetadata | None


class GetThread(Slack):
    TYPE = "scoutos:slack:get_thread"

    async def run(self, run_input: dict) -> GetThreadOutput:
        validated_input = GetThreadInput.model_validate(run_input)

        headers = self._headers
        params = validated_input.model_dump()
        url = f"{self._http_api_url}/conversations.replies"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()

                data = response.json()

                if not data.get("ok"):
                    message = data.get("error", "an unknown exception occurred")
                    raise BlockExecutionError(message)

                return data
                # return GetThreadOutput.model_validate(data)

            except ValidationError as validation_error:
                message = "output failed data validation"
                raise BlockExecutionError(message) from validation_error

            except httpx.HTTPStatusError as http_status_error:
                message = "http request failed"
                raise BlockExecutionError(message) from http_status_error
