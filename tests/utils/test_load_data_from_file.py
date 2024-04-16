import json
from pathlib import Path

import pytest
import yaml

from scoutos.utils import read_data_from_file

DATA_FOR_TEST_CASES = [
    {"foo": "baz"},
    {"one": {"two": "three"}},
    {
        "id": "APP-ID-1234",
        "tags": ["tag-one", "tag-two", "tag-three"],
        "blocks": [
            {"type": "scoutos_input"},
            {"type": "scoutos_output"},
        ],
    },
]


@pytest.fixture()
def with_json_file(tmp_path, request):
    data = request.param
    file_path = tmp_path / "sample_data.json"
    with Path.open(file_path, "w") as f:
        json.dump(data, f)

    return file_path


@pytest.fixture()
def with_yaml_file(tmp_path, request):
    data = request.param
    file_path = tmp_path / "sample_data.yaml"
    with Path.open(file_path, "w") as f:
        yaml.dump(data, f)

    return file_path


@pytest.fixture()
def with_yml_file(tmp_path, request):
    data = request.param
    file_path = tmp_path / "sample_data.yml"
    with Path.open(file_path, "w") as f:
        yaml.dump(data, f)

    return file_path


@pytest.fixture()
def with_txt_file(tmp_path, content: str):
    data = content
    file_path = tmp_path / "sample_data.txt"
    with Path.open(file_path, "w") as f:
        f.write(data)

    return file_path


@pytest.mark.parametrize(
    ("with_json_file", "expected_result"),
    [(data, data) for data in DATA_FOR_TEST_CASES],
    indirect=[
        "with_json_file",
    ],
)
def test_reading_from_json_file(with_json_file, expected_result):
    result = read_data_from_file(with_json_file)
    assert result == expected_result


@pytest.mark.parametrize(
    ("with_yaml_file", "expected_result"),
    [(data, data) for data in DATA_FOR_TEST_CASES],
    indirect=[
        "with_yaml_file",
    ],
)
def test_reading_from_yaml_file(with_yaml_file, expected_result):
    result = read_data_from_file(with_yaml_file)
    assert result == expected_result


@pytest.mark.parametrize(
    ("with_yml_file", "expected_result"),
    [(data, data) for data in DATA_FOR_TEST_CASES],
    indirect=[
        "with_yml_file",
    ],
)
def test_reading_from_yml_file(with_yml_file, expected_result):
    result = read_data_from_file(with_yml_file)
    assert result == expected_result


def test_reading_from_unknown_file_type_raises(tmp_path):
    file_path = tmp_path / "sample_data.txt"
    with Path.open(file_path, "w") as f:
        f.write("Lorem Ipsum")

    with pytest.raises(ValueError, match="No handler found for .txt filetype"):
        read_data_from_file(file_path)
