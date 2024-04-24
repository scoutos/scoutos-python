from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar

from typing_extensions import Required, TypedDict

from scoutos.constants import THE_START_OF_TIME_AND_SPACE
from scoutos.utils import DefaultValue, get_nested_value_from_dict

if TYPE_CHECKING:  # pragma: no cover
    from scoutos.blocks.base import BlockOutput


DEPENDENCY_TYPE_ATTR = "TYPE"
DEPENDENCY_TYPE_KEY = "type"


class DependencyMeta(ABCMeta):
    REGISTERED_DEPENDENCIES: ClassVar = {}

    def __new__(cls, name, bases, dct):  # noqa: ANN001
        dependency_cls = super().__new__(cls, name, bases, dct)

        if not dct.get("_is_base_class", False):
            dependency_type = dct.get(DEPENDENCY_TYPE_ATTR)
            if dependency_type is None or not isinstance(dependency_type, str):
                message = f"Expected {name} to define {DEPENDENCY_TYPE_ATTR} in {dct}"
                raise ValueError(message)

            cls.REGISTERED_DEPENDENCIES[dependency_type] = dependency_cls

        return dependency_cls


T = TypeVar("T")


class DependencyBaseConfig(Generic[T], TypedDict, total=False):
    path: Required[str]
    key: str
    default_value: T
    requires_rerun: bool


class Dependency(ABC, Generic[T], metaclass=DependencyMeta):
    _is_base_class = True

    @classmethod
    def load(cls, config: dict) -> Dependency:
        dependency_type = config.pop(DEPENDENCY_TYPE_KEY, None)
        if not dependency_type:
            message = f"Expected {DEPENDENCY_TYPE_KEY} to be provided"
            raise ValueError(message)

        dependency_cls = DependencyMeta.REGISTERED_DEPENDENCIES.get(dependency_type)
        if not dependency_cls:
            message = f"{dependency_type} is not registered"
            raise ValueError(message)

        return dependency_cls(config)

    def __init__(
        self,
        config: DependencyBaseConfig,
    ):
        """Express a dependency on the output of another block.

        path: str - the path to the dependency, separated by `.`
        """
        self._default_value: DefaultValue = DefaultValue(
            is_set=config.get("default_value") is not None,
            value=config.get("default_value"),
        )
        self._key = config.get("key", config["path"].split(".")[-1])
        self._path = config["path"]
        self._requires_rerun = config.get("requires_rerun", False)

    @property
    def block_id(self) -> str:
        """The ID of the block where this dependency is satisfied. It is the
        first component of the path."""
        return self._path.split(".")[0]

    @property
    def default_value(self) -> DefaultValue[T]:
        """The default_value if one has been provided."""
        return self._default_value

    @property
    def key(self) -> str:
        """The key under which this value will be passed-in."""
        return self._key

    @property
    def path(self) -> str:
        """The path to the value found in output. Note this does not include the
        block_id, which we provide separately."""
        segments = self._path.split(".")[1:]
        if len(segments) == 0:
            raise DependencyPathError

        return ".".join(segments)

    @property
    def requires_rerun(self) -> bool:
        """Returns True, if this dependency has been declared that it should be
        rerun each time it is to be resolved."""
        return self._requires_rerun

    def __str__(self):  # pragma: no cover
        return f"Dependency(block_id={self.block_id}, path={self.path}, key={self.key}, default_value={self.default_value})"  # noqa: E501

    def is_resolved(
        self,
        current_output: list[BlockOutput],
        *,
        since: str = THE_START_OF_TIME_AND_SPACE,
    ) -> bool:
        return (
            self.resolved_with(current_output, since=since) is not None
            or self.default_value.is_set
        )

    def resolved_with(
        self,
        current_output: list[BlockOutput],
        *,
        since: str,
    ) -> BlockOutput | None:
        for record in current_output[::-1]:
            if record.block_id == self.block_id and record.block_run_end_ts > since:
                return record

        return None

    def resolve(
        self, current_output: list[BlockOutput], *, since: str = "1970-01-01"
    ) -> T:
        """Given the `current_output` evaluate the value of the dependency if
        present. Raise if the dependency is not found and no default has been
        provided.
        """
        resolving_output = self.resolved_with(current_output, since=since)

        if resolving_output is None and not self.default_value.is_set:
            message = f"No result for {self.block_id} found"
            raise UnsatisfiedDependencyError(message)

        value = (
            get_nested_value_from_dict(self.path, resolving_output.output)
            if resolving_output
            else None
        )
        if value is None and self.default_value.is_set:
            value = self.default_value.value

        if value is None:
            message = f"No value found for path: {self.path}"
            raise UnsatisfiedDependencyError(message)

        return self.parse(value)

    @abstractmethod
    def parse(self, value: Any) -> T:  # noqa: ANN401
        """Parse and coerce the value according to the expected type. This
        method should raise if the value is not coercable."""
        ...  # pragma: no cover


class DependencyPathError(Exception):
    MESSAGE = "Path should have multiple segments"

    def __init__(self):
        super().__init__(self.MESSAGE)


class UnsatisfiedDependencyError(Exception):
    pass
