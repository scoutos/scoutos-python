from __future__ import annotations

from typing import Literal, Required

import httpx
import jinja2

from scoutos.blocks.base import Block, BlockBaseConfig

ALLOWED_METHOD_VERBS = Literal["GET", "POST"]


class HttpConfig(BlockBaseConfig, total=False):
    headers: dict[str, str] | None
    method: Literal["get", "post"]
    response_type: Literal["json", "text"]
    url: Required[str]


class Http(Block):
    TYPE = "scoutos_http"

    def __init__(self, config: HttpConfig):
        super().__init__(config)
        self._headers = config.get("headers", {})
        self._method = config.get("method", "get")
        self._response_type = config.get("response_type", "json")
        self._url = jinja2.Template(config["url"])

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
