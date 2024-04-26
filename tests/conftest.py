import json
import uuid
from pathlib import Path
from typing import Callable
from unittest.mock import patch

import pytest


@pytest.fixture(scope="session", autouse=True)
def freeze_uuid4():  # noqa: ANN201, PT004
    """
    Mock uuid.uuid4() to return a fixed UUID for all tests for reproducible
    results.
    """
    fixed_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
    with patch("uuid.uuid4", return_value=fixed_uuid):
        yield


@pytest.fixture()
def get_fixture_data() -> Callable[[str], dict]:
    def _get_fixture_data(filepath: str) -> dict:
        path = Path(filepath)

        with path.open("rb") as file_contents:
            return json.load(file_contents)

    return _get_fixture_data
