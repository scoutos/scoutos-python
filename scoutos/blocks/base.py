from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    TypeVar,
)
from uuid import uuid4

from typing_extensions import Required, TypedDict

from scoutos.dependencies.base import Dependency
from scoutos.utils import get_current_timestamp

RunInput = TypeVar("RunInput")
RunOutput = TypeVar("RunOutput")

RunUntil = Callable[[dict], bool]


class BlockBaseConfig(TypedDict, total=False):
    key: Required[str]
    """A key that uniquely identifies _this_ block."""

    depends: list[Dependency]
    """A list of other blocks, identified by their keys, that _this_ block
    depends upon."""

    max_runs: int
    """If the block is potentially repeated, this represents the maximum number
    of times the block can be run, to prevent runaway processes (default = 10).
    """

    input_schema: dict[str, Any]
    """JSON Schema for input"""

    output_schema: dict[str, Any]
    """JSON Schema for output"""

    run_until: RunUntil
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


BLOCK_TYPE_ATTR = "TYPE"
BLOCK_TYPE_KEY = "type"


class BlockMeta(ABCMeta):
    REGISTERED_BLOCKS: ClassVar = {}

    def __new__(cls, name, bases, dct):  # noqa: ANN001
        block_cls = super().__new__(cls, name, bases, dct)

        if not dct.get("_is_base_class", False):
            block_type = dct.get(BLOCK_TYPE_ATTR)
            if block_type is None or not isinstance(block_type, str):
                message = f"Expected {name} to define {BLOCK_TYPE_ATTR} in {dct}"
                raise TypeError(message)

            cls.REGISTERED_BLOCKS[block_type] = block_cls

        return block_cls


class Block(ABC, Generic[RunInput, RunOutput], metaclass=BlockMeta):
    """This is the base block that all other Blocks will inherit from."""

    DEFAULT_MAX_RUNS = 10

    _initialized_with_super = False
    _is_base_class = True

    def __init__(self, config: BlockBaseConfig):
        self._initialized_with_super = True
        if not config.get("key"):
            message = "Requires `key` to be provided"
            raise TypeError(message)

        self._config = config
        self._output: list[BlockOutput[RunOutput]] = []

    @classmethod
    def load(cls, config: dict) -> Block:
        block_type = config.pop(BLOCK_TYPE_KEY, None)
        if not block_type:
            message = f"Expected {BLOCK_TYPE_KEY} to be provided"
            raise TypeError(message)

        block_cls = BlockMeta.REGISTERED_BLOCKS.get(block_type)
        if not block_cls:
            message = f"{block_type} is not registered"
            raise ValueError(message)

        config["depends"] = [
            Dependency.load(dep_data) for dep_data in config.get("depends", [])
        ]

        return block_cls(config)

    @property
    def depends(self) -> list[Dependency]:
        return self._config.get("depends", [])

    @property
    def has_exceeded_run_count(self) -> bool:
        return self.run_count >= self.max_runs

    @property
    def key(self) -> str:
        """Key that uniquely identifies _this_ block."""
        return self._config["key"]

    @property
    def last_run_completed_at(self) -> str | None:
        """Returns a string representation of a timestamp of when the last run
        for this block was completed at."""
        if len(self.output) == 0:
            return None

        return self.output[-1].block_run_end_ts

    @property
    def max_runs(self) -> int:
        return self._config.get("max_runs", self.DEFAULT_MAX_RUNS)

    @property
    def output(self) -> list[BlockOutput[RunOutput]]:
        return self._output

    @property
    def run_count(self) -> int:
        return len(self._output)

    @property
    def run_until(self) -> RunUntil:
        return self._config.get("run_until", lambda _data: True)

    def has_met_termination_condition(self, current_output: list[BlockOutput]) -> bool:
        return (
            not self.requires_rerun(current_output) or self.run_count >= self.max_runs
        )

    def resolve_deps(self, block_output: list[BlockOutput]) -> dict:
        return {dep.key: dep.resolve(block_output) for dep in self.depends}

    def requires_rerun(self, current_output: list[BlockOutput]) -> bool:
        data = self.resolve_deps(current_output)
        return not self.run_until(data)

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

    @property
    def input_schema(self) -> dict[str, Any]:
        """Returns valid JSON Schema representing the input required for run method"""
        return self._config.get("input_schema", {})

    @property
    def output_schema(self) -> dict[str, Any]:
        """Returns valid JSON Schema representing the output generated by the
        run method"""
        return self._config.get("output_schema", {})

    @abstractmethod
    async def run(self, run_input: dict) -> RunOutput:
        """Run the block. This is the meat and potatos. Yum yum."""


class BlockExecutionError(Exception):
    """Raised when a block raises during execution"""


class BlockInitializationError(Exception):
    """This is raised when blocks have not been initialized correctly."""

    MESSAGE = """
    Super class has not been initialized.

    In your block's `__init__` method you need to invoke
    `super().__init__(key="your_block_key")`
    """

    def __init__(self):
        super().__init__(self.MESSAGE)
