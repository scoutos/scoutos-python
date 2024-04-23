import pytest

from scoutos import Depends
from scoutos.dependencies import Dependency, UnsatisfiedDependencyError


def create_dependency():
    path = "block_id.nested.path"
    return Depends.IntType({"path": path})


def test_instantiation():
    obj = create_dependency()
    assert isinstance(obj, Dependency)
    assert isinstance(obj, Depends.IntType)


def test_parse_when_valid():
    dep = create_dependency()
    value = 42
    result = dep.parse(value)
    assert result == value


def test_parse_when_invalid():
    dep = create_dependency()
    value = "A very interesting journey"

    with pytest.raises(UnsatisfiedDependencyError):
        dep.parse(value)
