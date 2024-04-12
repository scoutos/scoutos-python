import pytest

from scoutos.env import get_env


def test_get_env(monkeypatch):
    key = "SOME_ENV_VAR"
    expected_value = "the-value"

    monkeypatch.setenv(key, expected_value)

    assert get_env(key) == expected_value


def test_get_env_raises_when_missing():
    with pytest.raises(KeyError):
        get_env("NON_EXISTENT_ENV_VAR")


def test_get_env_uses_default():
    supplied_default_value = "a-default-value"
    assert (
        get_env("NON_EXISTENT_ENV_VAR", default_value=supplied_default_value)
        == supplied_default_value
    )
