from typing import Any

from scoutos.dependencies.base import Dependency, UnsatisfiedDependencyError


class AnyDependency(Dependency[Any]):
    def parse(self, value: Any) -> Any:  # noqa: ANN401
        if value is None:
            message = f"Value not found for path ({self.block_id}.{self.path})"
            raise UnsatisfiedDependencyError(message)

        return value
