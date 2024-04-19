from __future__ import annotations

from typing import Literal, Unpack

import httpx
import jinja2

from scoutos.blocks.base import Block, BlockCommonArgs

ALLOWED_METHOD_VERBS = Literal["GET", "POST"]


class Http(Block):
    TYPE = "scoutos_http"

    def __init__(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        method: Literal["get", "post"] = "get",
        response_type: Literal["json", "text"] = "json",
        **kwargs: Unpack[BlockCommonArgs],
    ):
        super().__init__(**kwargs)
        self._headers = headers or {}
        self._method = method
        self._response_type = response_type
        self._url = jinja2.Template(url)

    async def run(self, run_input: dict) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                self._method,
                self._url.render(run_input),
                data=run_input,
                headers=self._headers,
            )

        if self._response_type == "json":
            return {"result": response.json()}

        return {"result": response.text}
