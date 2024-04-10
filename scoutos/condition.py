from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:  # pragma: no cover
    from scoutos.blocks.base import BlockOutput
    from scoutos.dependencies.base import Dependency


@dataclass
class Condition:
    fn: Callable[..., bool]
    depends: list[Dependency]

    def is_satisfied(self, current_output: list[BlockOutput]) -> bool:
        resolved_dependencies = [dep.resolve(current_output) for dep in self.depends]
        return self.fn(*resolved_dependencies)
