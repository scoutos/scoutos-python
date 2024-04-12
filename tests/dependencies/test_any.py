import pytest

from scoutos import Depends
from scoutos.dependencies import Dependency, UnsatisfiedDependencyError


def test_instantiation():
    obj = Depends.AnyType(path="some_block.some.path")
    assert isinstance(obj, Dependency)
    assert isinstance(obj, Depends.AnyType)


def test_parse():
    obj = Depends.AnyType(path="some_block.some.path")
    value = {"some": "obj", "with": "keys", "answer": 42}
    result = obj.parse(value)
    assert result == value


def test_raises_if_value_is_none():
    obj = Depends.AnyType(path="some_block.some.path")

    with pytest.raises(UnsatisfiedDependencyError):
        obj.parse(None)
