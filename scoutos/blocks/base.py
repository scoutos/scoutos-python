from abc import ABC, abstractmethod


class Block(ABC):
    """This is the base block that all other Blocks will inherit from."""

    @property
    @abstractmethod
    def key(self) -> str:
        """Key uniquely identifies _this_ block."""

    @abstractmethod
    async def run(self, run_input: dict) -> dict:
        """Run the block. This is the meat and potatos. Yum yum."""
