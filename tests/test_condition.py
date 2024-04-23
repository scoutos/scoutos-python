import pytest

from scoutos import Condition, Depends
from scoutos.blocks.base import BlockOutput


def create_block_output(block_id: str, output: dict) -> BlockOutput:
    return BlockOutput(
        block_id=block_id,
        block_run_id="BLOCK-RUN-ID-1234",
        block_run_end_ts="1970-01-01T00:00:000Z",
        block_run_start_ts="1970-01-01T00:00:000Z",
        ok=True,
        output=output,
    )


def test_instantiation():
    threshold = 5

    def word_count_greater_than_threshold(*args: str) -> bool:
        return len(args) > threshold

    condition = Condition(
        fn=word_count_greater_than_threshold,
        depends=[],
    )

    assert isinstance(condition, Condition)


@pytest.mark.parametrize(
    ("fn", "deps", "current_output", "expected_result"),
    [
        (
            lambda n, count: count >= n,
            [
                Depends.IntType({"path": "input.n"}),
                Depends.IntType({"path": "counter.count", "default_value": 0}),
            ],
            [
                create_block_output("input", {"n": 5}),
                create_block_output("counter", {"count": 1}),
            ],
            False,
        ),
        (
            lambda n, count: count >= n,
            [
                Depends.IntType({"path": "input.n"}),
                Depends.IntType({"path": "counter.count", "default_value": 0}),
            ],
            [
                create_block_output("input", {"n": 5}),
            ],
            False,
        ),
        (
            lambda n, count: count >= n,
            [
                Depends.IntType({"path": "input.n"}),
                Depends.IntType({"path": "counter.count", "default_value": 0}),
            ],
            [
                create_block_output("input", {"n": 5}),
                create_block_output("counter", {"count": 5}),
            ],
            True,
        ),
    ],
)
def test_is_satisfied(fn, deps, current_output, expected_result):
    condition = Condition(fn, depends=deps)
    assert condition.is_satisfied(current_output) == expected_result
