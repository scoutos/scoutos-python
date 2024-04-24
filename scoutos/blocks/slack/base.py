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
        self._config = config
