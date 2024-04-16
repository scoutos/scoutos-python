from typing import Any, Unpack

import pytest

from scoutos.blocks.base import BlockOutput
from scoutos.dependencies.base import (
    Dependency,
    DependencyOptions,
    DependencyPathError,
    UnsatisfiedDependencyError,
)


def create_block_run_output(block_id: str, output: dict) -> BlockOutput:
    return BlockOutput(
        block_id=block_id,
        block_run_id="BLOCK-RUN-ID-1234",
        block_run_start_ts="1970-01-01T00:00:000Z",
        block_run_end_ts="1970-01-01T00:00:000Z",
        ok=True,
        output=output,
    )


def create_dependency(path: str, **kwargs: Unpack[DependencyOptions]) -> Dependency:
    class StubbedStrDependency(Dependency[str]):
        TYPE = "stubbed_str_dep"

        def parse(self, value: Any) -> str:
            return str(value)

    return StubbedStrDependency(path, **kwargs)


def test_it_loads_from_valid_data():
    class SomeDependency(Dependency[str]):
        TYPE = "scoutos_some_dependency"

        def parse(self, value: Any) -> str:
            return str(value)

    data = {
        "type": SomeDependency.TYPE,
        "path": "block_id.some.path",
    }

    obj = Dependency.load(data)

    assert isinstance(obj, Dependency)
    assert isinstance(obj, SomeDependency)


def test_class_raises_on_initlialization_if_missing_dep_type():
    with pytest.raises(ValueError, match="define TYPE"):

        class InvalidDep(Dependency[str]):
            def parse(self, value: Any) -> str:
                return str(value)


def test_raises_on_load_if_missing_type():
    class SomeDependency(Dependency[str]):
        TYPE = "scoutos_some_dependency"

        def parse(self, value: Any) -> str:
            return str(value)

    data = {
        "path": "block_id.some.path",
    }

    with pytest.raises(ValueError, match="Expected type to be provided"):
        Dependency.load(data)


def test_it_raises_when_unregistered_dep_specified():
    data = {
        "type": "unregistered_block_type",
        "path": "block_id.some.path",
    }

    with pytest.raises(ValueError, match="not registered"):
        Dependency.load(data)


@pytest.mark.parametrize(
    ("path", "expected_result"),
    [
        ("input.first_name", "input"),
        ("some_block_id.some.nested.path", "some_block_id"),
    ],
)
def test_block_id(path, expected_result):
    dep = create_dependency(path)
    assert dep.block_id == expected_result


@pytest.mark.parametrize(
    ("opts", "expected_result"),
    [
        ({"default_value": "foo"}, "foo"),
        ({}, None),
    ],
)
def test_default_value(opts, expected_result):
    dep = create_dependency("block_id.some.path", **opts)
    assert dep.default_value.value == expected_result


@pytest.mark.parametrize(
    ("path", "opts", "expected_result"),
    [
        ("block_id.key", {}, "key"),
        ("block_id.key_from_path", {"key": "key_from_opts"}, "key_from_opts"),
    ],
)
def test_key(path, opts, expected_result):
    dep = create_dependency(path, **opts)
    assert dep.key == expected_result


@pytest.mark.parametrize(
    ("path", "expected_result"),
    [
        ("block_id.path", "path"),
        ("block_id.nested.path", "nested.path"),
    ],
)
def test_path(path, expected_result):
    dep = create_dependency(path)
    assert dep.path == expected_result


def test_path_raises_if_not_multiple_segments():
    dep = create_dependency("single_segment")

    with pytest.raises(DependencyPathError):
        dep.path  # noqa: B018


@pytest.mark.parametrize(
    ("current_output", "path", "init_opts", "expected_result"),
    [
        ([], "some_block.some.path", {}, False),
        ([], "some_block.some.path", {"default_value": "foo"}, True),
        (
            [create_block_run_output("input", {"foo": "baz"})],
            "input.key",
            {},
            True,
        ),
        (
            [create_block_run_output("input", {"foo": "baz"})],
            "input.fizz",
            {"default_value": "buzz"},
            True,
        ),
    ],
)
def test_is_resolved(current_output, path, init_opts, expected_result):
    dep = create_dependency(path, **init_opts)
    result = dep.is_resolved(current_output)
    assert result == expected_result


@pytest.mark.parametrize(
    ("current_output", "path", "init_opts", "expected_result"),
    [
        ([], "some_block.some.path", {"default_value": "foo"}, "foo"),
        (
            [create_block_run_output("input", {"foo": "baz"})],
            "input.foo",
            {},
            "baz",
        ),
        (
            [create_block_run_output("input", {"foo": "baz"})],
            "input.fizz",
            {"default_value": "buzz"},
            "buzz",
        ),
    ],
)
def test_resolve(current_output, path, init_opts, expected_result):
    dep = create_dependency(path, **init_opts)
    result = dep.resolve(current_output)
    assert result == expected_result


def test_raises_on_resolve_with_no_corresponding_output():
    dep = create_dependency("non_existent_block_id.some.path")

    with pytest.raises(UnsatisfiedDependencyError):
        dep.resolve([])


def test_raises_on_resolve_with_missing_value():
    dep = create_dependency("input.fizz")
    current_output = [create_block_run_output("input", {"foo": "baz"})]

    with pytest.raises(UnsatisfiedDependencyError):
        dep.resolve(current_output)
