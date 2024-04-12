from types import SimpleNamespace

from .any import AnyDependency
from .bool import BoolDependency
from .float import FloatDependency
from .int import IntDependency
from .str import StrDependency

Depends = SimpleNamespace(
    AnyType=AnyDependency,
    BoolType=BoolDependency,
    FloatType=FloatDependency,
    IntType=IntDependency,
    StrType=StrDependency,
)
