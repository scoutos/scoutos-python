from freezegun import freeze_time

from scoutos.utils import get_current_timestamp


@freeze_time("1970-01-01")
def test_get_current_timestamp():
    expected = "1970-01-01T00:00:00Z"
    result = get_current_timestamp()

    assert result == expected
