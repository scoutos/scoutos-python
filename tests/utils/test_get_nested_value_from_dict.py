import pytest

from scoutos.utils import get_nested_value_from_dict


@pytest.mark.parametrize(
    ("path", "the_dict", "expected_value"),
    [
        ("foo", {"foo": 42}, 42),
        ("non_existent_key", {"foo": 42}, None),
        (
            "level_one.level_two.level_three",
            {"level_one": {"level_two": {"level_three": 42}}},
            42,
        ),
        (
            "level_one.level_two.level_three.level_four",
            {
                "level_one": {
                    "level_two": {
                        "level_three": None,
                    }
                }
            },
            None,
        ),
        (
            "level_one.level_two.level_three.level_four",
            {
                "level_one": {
                    "level_two": {
                        "level_three": [],
                    }
                }
            },
            None,
        ),
        (
            "foo",
            {
                "foo": {},
            },
            {},
        ),
    ],
)
def test_it_returns_value_when_present(path, the_dict, expected_value):
    result = get_nested_value_from_dict(path, the_dict)

    assert result == expected_value
