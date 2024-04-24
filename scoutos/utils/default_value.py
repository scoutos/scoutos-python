from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class DefaultValue(Generic[T]):
    is_set: bool
    value: T | None
