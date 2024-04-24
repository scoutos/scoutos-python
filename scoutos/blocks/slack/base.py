from typing import TypeVar

from scoutos.blocks import Block, BlockBaseConfig

RunInput = TypeVar("RunInput")
RunOutput = TypeVar("RunOutput")


class SlackConfig(BlockBaseConfig):
    token: str
    """Slack token required to interact with API"""


class Slack(Block[RunInput, RunOutput]):
    _is_base_class = True

    def __init__(self, config: SlackConfig):
        super().__init__(config)
        self._config: SlackConfig = config

    @property
    def _http_api_url(self) -> str:
        return "https://slack.com/api"

    @property
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._config['token']}"}
