import pytest

from scoutos import hello_world


@pytest.mark.parametrize(
    ("name", "expected"),
    [("you", "Hello, You!"), ("Sammy", "Hello, Sammy!"), ("world", "Hello, World!")],
)
def test_hello_world_with_input(name, expected):
    result = hello_world(name)
    assert result == expected


def test_hello_world_with_no_input():
    expected = "Hello, You!"
    result = hello_world()

    assert result == expected
