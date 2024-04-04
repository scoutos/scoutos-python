from typing import Any

from pydantic import TypeAdapter, ValidationError

from scoutos.dependencies.base import Dependency, UnsatisfiedDependencyError


class BoolDependency(Dependency[bool]):
    adapter = TypeAdapter(bool)

    def parse(self, value: Any) -> bool:  # noqa: ANN401
        try:
            return self.adapter.validate_python(value)
        except ValidationError as original_exception:
            message = f"Unalbe to coerce value at {self.path} into bool"
            raise UnsatisfiedDependencyError(message) from original_exception
