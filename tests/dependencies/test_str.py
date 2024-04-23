import pytest

from scoutos import Depends
from scoutos.dependencies import Dependency, UnsatisfiedDependencyError


def create_dependency():
    path = "block_id.nested.path"
    return Depends.StrType({"path": path})


def test_instantiation():
    obj = create_dependency()
    assert isinstance(obj, Dependency)
    assert isinstance(obj, Depends.StrType)


def test_parse_when_valid():
    dep = create_dependency()
    value = "Forty-Two"
    result = dep.parse(value)
    assert result == value


def test_parse_when_invalid():
    dep = create_dependency()
    value = 42

    with pytest.raises(UnsatisfiedDependencyError):
        dep.parse(value)
