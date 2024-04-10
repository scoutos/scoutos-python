from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Callable,
    Generic,
    Required,
    TypedDict,
    TypeVar,
    Unpack,
)
from uuid import uuid4

from scoutos.utils import get_current_timestamp

if TYPE_CHECKING:  # pragma: no cover
    from scoutos.dependencies.base import Dependency

RunInput = TypeVar("RunInput")
RunOutput = TypeVar("RunOutput")


class BlockCommonArgs(TypedDict, total=False):
    key: Required[str]
    """A key that uniquely identifies _this_ block."""

    depends: list[Dependency]
    """A list of other blocks, identified by their keys, that _this_ block
    depends upon."""

    run_until: Callable[[dict], bool]
    """If provided, this repersents a condition that while false, will cause the
    block to re-execute."""


@dataclass
class BlockOutput(Generic[RunOutput]):
    """Structured output returned at the termination of each block run."""

    block_id: str
    block_run_id: str
    block_run_start_ts: str
    block_run_end_ts: str
    ok: bool
    output: RunOutput


class Block(ABC, Generic[RunInput, RunOutput]):
    """This is the base block that all other Blocks will inherit from."""

    _initialized_with_super = False

    def __init__(self, **kwargs: Unpack[BlockCommonArgs]):
        self._key = kwargs["key"]
        self._depends = kwargs.get("depends", [])
        self._run_until = kwargs.get("run_until", lambda _data: True)
        self._initialized_with_super = True

    @property
    def depends(self) -> list[Dependency]:
        return self._depends

    @property
    def key(self) -> str:
        """Key that uniquely identifies _this_ block."""
        return self._key

    @abstractmethod
    async def run(self, run_input: dict) -> RunOutput:
        """Run the block. This is the meat and potatos. Yum yum."""

    def resolve_deps(self, block_output: list[BlockOutput]) -> dict:
        return {dep.key: dep.resolve(block_output[::-1]) for dep in self.depends}

    def requires_rerun(self, current_output: list[BlockOutput]) -> bool:
        data = self.resolve_deps(current_output)
        return not self._run_until(data)

    async def outter_run(
        self,
        current_state: list[BlockOutput],
        *,
        override_input: dict | None = None,
    ) -> BlockOutput[RunOutput]:
        """Outter wrapper for the subclasses run method.

        We use this to apply common patterns and to validate any global
        requirements.
        """
        if not self._initialized_with_super:
            raise BlockInitializationError

        block_run_start_ts = get_current_timestamp()
        block_run_id = str(uuid4())
        block_input = override_input or self.resolve_deps(current_state)
        output = await self.run(block_input)
        block_run_end_ts = get_current_timestamp()

        return BlockOutput(
            ok=True,
            block_id=self.key,
            block_run_id=block_run_id,
            block_run_start_ts=block_run_start_ts,
            block_run_end_ts=block_run_end_ts,
            output=output,
        )


class BlockInitializationError(Exception):
    """This is raised when blocks have not been initialized correctly."""

    MESSAGE = """
    Super class has not been initialized.

    In your block's `__init__` method you need to invoke
    `super().__init__(key="your_block_key")`
    """

    def __init__(self):
        super().__init__(self.MESSAGE)
