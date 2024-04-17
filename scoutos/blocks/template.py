from typing import Unpack

from jinja2 import Template as JinjaTemplate

from scoutos.blocks import Block, BlockCommonArgs


class Template(Block):
    TYPE = "scoutos_template"

    def __init__(self, *, template: str, **kwargs: Unpack[BlockCommonArgs]):
        super().__init__(**kwargs)
        self._template = JinjaTemplate(template)

    async def run(self, run_input: dict) -> dict:
        return {"result": self._template.render(run_input)}
