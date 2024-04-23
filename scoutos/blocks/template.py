from typing import Required

from jinja2 import Template as JinjaTemplate

from scoutos.blocks import Block, BlockBaseConfig


class TemplateConfig(BlockBaseConfig):
    template: Required[str]
    """The Jinja template to be applied to the input when run"""


class Template(Block):
    TYPE = "scoutos_template"

    def __init__(self, config: TemplateConfig):
        super().__init__(config)
        self._template = JinjaTemplate(config["template"])

    async def run(self, run_input: dict) -> dict:
        return {"result": self._template.render(run_input)}
