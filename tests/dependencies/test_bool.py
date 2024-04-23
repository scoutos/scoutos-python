import pytest

from scoutos import Depends
from scoutos.dependencies import Dependency, UnsatisfiedDependencyError


def test_instantiation():
    obj = Depends.BoolType({"path": "block_id.nested.path"})
    assert isinstance(obj, Dependency)
    assert isinstance(obj, Depends.BoolType)


def test_parse_when_valid():
    dep = Depends.BoolType({"path": "block_id.nested.path"})
    value = True
    result = dep.parse(value)
    assert result == value


def test_parse_when_invalid():
    dep = Depends.BoolType({"path": "block_id.nested.path"})
    value = "A very interesting journey"

    with pytest.raises(UnsatisfiedDependencyError):
        dep.parse(value)
