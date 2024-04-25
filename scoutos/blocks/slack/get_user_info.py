import httpx
from pydantic import TypeAdapter, ValidationError
from typing_extensions import TypedDict

from scoutos.blocks import BlockExecutionError

from .base import Slack


class GetUserInfoInput(TypedDict):
    user_id: str


class GetUserInfoOutput(TypedDict):
    deleted: bool
    id: str
    is_admin: bool
    is_bot: bool
    is_owner: bool
    is_primary_owner: bool
    name: str
    real_name: str
    team_id: str


input_adapter = TypeAdapter(GetUserInfoInput)
output_adapter = TypeAdapter(GetUserInfoOutput)


class GetUserInfo(Slack):
    TYPE = "scoutos:slack:get_user_info"

    async def run(self, run_input: dict) -> GetUserInfoOutput:
        validated_input = input_adapter.validate_python(run_input)

        headers = self._headers
        params = {"user": validated_input["user_id"]}
        url = f"{self._http_api_url}/users.info"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()

                data = response.json()

                if not data.get("ok"):
                    message = data.get("error", "An unknown exception occurred")
                    raise BlockExecutionError(message)

                return output_adapter.validate_python(data.get("user", {}))

            except ValidationError as validation_error:
                message = "output failed data validation"
                raise BlockExecutionError(message) from validation_error
            except httpx.HTTPStatusError as http_status_error:
                message = "http request failed"
                raise BlockExecutionError(message) from http_status_error
