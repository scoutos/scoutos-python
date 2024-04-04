import uuid
from unittest.mock import patch

import pytest
from freezegun import freeze_time


@pytest.fixture(scope="session", autouse=True)
def freeze_time_for_tests():  # noqa: ANN201, PT004
    """
    Freeze time at a specific point across all tests for reproducible
    timestamps.
    """
    frozen_time = "1970-01-01"
    with freeze_time(frozen_time):
        yield


@pytest.fixture(scope="session", autouse=True)
def freeze_uuid4():  # noqa: ANN201, PT004
    """
    Mock uuid.uuid4() to return a fixed UUID for all tests for reproducible
    results.
    """
    fixed_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
    with patch("uuid.uuid4", return_value=fixed_uuid):
        yield
