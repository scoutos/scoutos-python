from scoutos.utils import get_current_timestamp


def test_get_current_timestamp():
    expected = "1970-01-01T00:00:00Z"
    result = get_current_timestamp()

    assert result == expected
