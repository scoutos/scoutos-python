from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Callable,
    ClassVar,
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

    max_runs: int
    """If the block is potentially repeated, this represents the maximum number
    of times the block can be run, to prevent runaway processes (default = 10).
    """

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


BLOCK_TYPE_KEY = "BLOCK_TYPE"


class BlockMeta(ABCMeta):
    REGISTERED_BLOCKS: ClassVar = {}

    def __new__(cls, name, bases, dct):  # noqa: ANN001
        block_cls = super().__new__(cls, name, bases, dct)

        if not dct.get("_is_base_class", False):
            block_type = dct.get(BLOCK_TYPE_KEY)
            if block_type is None or not isinstance(block_type, str):
                message = f"Expected {name} to define {BLOCK_TYPE_KEY} in {dct}"
                raise ValueError(message)

            cls.REGISTERED_BLOCKS[block_type] = block_cls

        return block_cls


class Block(ABC, Generic[RunInput, RunOutput], metaclass=BlockMeta):
    """This is the base block that all other Blocks will inherit from."""

    DEFAULT_MAX_RUNS = 10

    _initialized_with_super = False
    _is_base_class = True

    def __init__(self, **kwargs: Unpack[BlockCommonArgs]):
        self._initialized_with_super = True
        self._key = kwargs["key"]
        self._depends = kwargs.get("depends", [])
        self._run_until = kwargs.get("run_until", lambda _data: True)
        self._max_runs = kwargs.get("max_runs", self.DEFAULT_MAX_RUNS)
        self._output: list[BlockOutput[RunOutput]] = []

    @classmethod
    def load(cls, data: dict) -> Block:
        block_type_key = "block_type"
        block_type = data.get(block_type_key)
        if not block_type:
            message = f"Expected {block_type_key} to be provided"
            raise ValueError(message)

        block_cls = BlockMeta.REGISTERED_BLOCKS.get(block_type)
        if not block_cls:
            message = f"{block_type} is not registered"
            raise ValueError(message)

        data.pop(block_type_key)
        return block_cls(**data)

    @property
    def depends(self) -> list[Dependency]:
        return self._depends

    @property
    def has_exceeded_run_count(self) -> bool:
        return self.run_count >= self.max_runs

    @property
    def key(self) -> str:
        """Key that uniquely identifies _this_ block."""
        return self._key

    @property
    def last_run_completed_at(self) -> str | None:
        """Returns a string representation of a timestamp of when the last run
        for this block was completed at."""
        if len(self.output) == 0:
            return None

        return self.output[-1].block_run_end_ts

    @property
    def max_runs(self) -> int:
        return self._max_runs

    @property
    def output(self) -> list[BlockOutput[RunOutput]]:
        return self._output

    @property
    def run_count(self) -> int:
        return len(self._output)

    def has_met_termination_condition(self, current_output: list[BlockOutput]) -> bool:
        return (
            not self.requires_rerun(current_output) or self.run_count >= self.max_runs
        )

    @abstractmethod
    async def run(self, run_input: dict) -> RunOutput:
        """Run the block. This is the meat and potatos. Yum yum."""

    def resolve_deps(self, block_output: list[BlockOutput]) -> dict:
        return {dep.key: dep.resolve(block_output) for dep in self.depends}

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

        run_output = BlockOutput(
            ok=True,
            block_id=self.key,
            block_run_id=block_run_id,
            block_run_start_ts=block_run_start_ts,
            block_run_end_ts=block_run_end_ts,
            output=output,
        )

        self._output.append(run_output)

        return run_output


class BlockInitializationError(Exception):
    """This is raised when blocks have not been initialized correctly."""

    MESSAGE = """
    Super class has not been initialized.

    In your block's `__init__` method you need to invoke
    `super().__init__(key="your_block_key")`
    """

    def __init__(self):
        super().__init__(self.MESSAGE)
