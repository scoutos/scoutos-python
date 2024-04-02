from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class BlockOutput:
    """Structured output returned at the termination of each block run."""

    ok: bool
    output: dict


class Block(ABC):
    """This is the base block that all other Blocks will inherit from."""

    _initialized_with_super = False

    def __init__(self, *, key: str):
        self._key = key
        self._initialized_with_super = True

    @property
    def key(self) -> str:
        """Key that uniquely identifies _this_ block."""
        return self._key

    @abstractmethod
    async def run(self, run_input: dict) -> dict:
        """Run the block. This is the meat and potatos. Yum yum."""

    async def wrapped_run(self, run_input: dict) -> BlockOutput:
        """Outter wrapper for the subclasses run method.

        We use this to apply common patterns and to validate any global
        requirements.
        """
        if not self._initialized_with_super:
            raise BlockInitializationError

        output = await self.run(run_input)

        return BlockOutput(ok=True, output=output)


class BlockInitializationError(Exception):
    """This is raised when blocks have not been initialized correctly."""

    MESSAGE = """
    Super class has not been initialized.

    In your block's `__init__` method you need to invoke
    `super().__init__(key="your_block_key")`
    """

    def __init__(self):
        super().__init__(self.MESSAGE)
