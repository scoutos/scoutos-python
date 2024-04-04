from typing import Any

from pydantic import TypeAdapter, ValidationError

from scoutos.dependencies.base import Dependency, UnsatisfiedDependencyError


class IntDependency(Dependency[int]):
    adapter = TypeAdapter(int)

    def parse(self, value: Any) -> int:  # noqa: ANN401
        try:
            return self.adapter.validate_python(value)
        except ValidationError as original_exception:
            message = f"Unalbe to coerce value at {self.path} into int"
            raise UnsatisfiedDependencyError(message) from original_exception
